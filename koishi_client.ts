import { Context, Schema, Logger } from 'koishi'
import * as fs from 'fs'
import * as path from 'path'

export const name = 'steamdt-client'
export const usage = `
SteamDT 异动数据爬虫客户端

支持的指令：
- /scrape [scrolls] [priority] - 添加爬取任务
- /queue - 查看队列状态
- /task [task_id] - 查看任务结果
- /image [task_id] - 获取任务图片
- /health - 健康检查
- /steamdt test - 测试API连接
`

export interface Config {
  apiUrl: string
  timeout: number
  retryAttempts: number
  retryDelay: number
  enableDetailedLogging: boolean
}

export const Config: Schema<Config> = Schema.object({
  apiUrl: Schema.string()
    .default('http://127.0.0.1:1145')
    .description('API服务地址（如 http://127.0.0.1:1145）')
    .role('url'),
  timeout: Schema.number()
    .default(30000)
    .min(1000)
    .max(300000)
    .description('请求超时时间（毫秒，1000-300000）'),
  retryAttempts: Schema.number()
    .default(3)
    .min(0)
    .max(10)
    .description('网络失败重试次数（0-10）'),
  retryDelay: Schema.number()
    .default(1000)
    .min(100)
    .max(10000)
    .description('重试延迟时间（毫秒，100-10000）'),
  enableDetailedLogging: Schema.boolean()
    .default(false)
    .description('启用详细日志（用于调试）'),
}).description('基础配置')

const logger = new Logger('steamdt-client')

interface TaskResult {
  task_id: number
  scrolls: number
  priority: number
  created_at: string
  started_at?: string
  completed_at?: string
  status: string
  result?: {
    up_count: number
    down_count: number
    total_count: number
    avg_up_percent: number
    avg_down_percent: number
    image_path: string
  }
  error?: string
}

interface QueueStatus {
  queue_length: number
  current_task?: {
    scrolls: number
    priority: number
    created_at: string
    status: string
  }
  completed_count: number
  queue: Array<{
    scrolls: number
    priority: number
    created_at: string
    status: string
  }>
}

interface HealthStatus {
  status: string
  queue_length: number
  completed_tasks: number
  timestamp: string
}

export function apply(ctx: Context, config: Config) {
  const apiUrl = config.apiUrl.replace(/\/$/, '')
  const timeout = config.timeout
  const retryAttempts = config.retryAttempts
  const retryDelay = config.retryDelay
  const enableDetailedLogging = config.enableDetailedLogging

  logger.info(`SteamDT客户端已加载，API地址: ${apiUrl}，重试次数: ${retryAttempts}，超时: ${timeout}ms`)

  /**
   * 日志辅助函数
   */
  function logDebug(message: string, data?: any) {
    if (enableDetailedLogging) {
      logger.debug(`[DEBUG] ${message}${data ? ': ' + JSON.stringify(data) : ''}`)
    }
  }

  function logInfo(message: string, data?: any) {
    logger.info(`[INFO] ${message}${data ? ': ' + JSON.stringify(data) : ''}`)
  }

  function logWarn(message: string, data?: any) {
    logger.warn(`[WARN] ${message}${data ? ': ' + JSON.stringify(data) : ''}`)
  }

  function logError(message: string, error?: any) {
    const errorMsg = error?.message || String(error)
    logger.error(`[ERROR] ${message}: ${errorMsg}`)
    if (enableDetailedLogging && error?.stack) {
      logger.debug(`[STACK] ${error.stack}`)
    }
  }

  /**
   * 发送HTTP请求的辅助函数（带重试机制）
   */
  async function fetchAPI(endpoint: string, method: string = 'GET', body?: any): Promise<any> {
    let lastError: any = null

    for (let attempt = 1; attempt <= retryAttempts; attempt++) {
      try {
        const url = `${apiUrl}${endpoint}`
        logDebug(`[${method}] ${url} (尝试 ${attempt}/${retryAttempts})`)

        const options: any = {
          method,
          timeout,
          headers: {
            'Content-Type': 'application/json',
          },
        }

        if (body) {
          options.body = JSON.stringify(body)
          logDebug(`请求体`, body)
        }

        const startTime = Date.now()
        const response = await fetch(url, options)
        const duration = Date.now() - startTime

        logDebug(`响应状态: ${response.status}，耗时: ${duration}ms`)

        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`)
        }

        const contentType = response.headers.get('content-type')
        let data: any

        if (contentType?.includes('application/json')) {
          data = await response.json()
          logDebug(`JSON响应`, data)
        } else if (contentType?.includes('image')) {
          const contentLength = response.headers.get('content-length')
          logDebug(`收到图片数据，大小: ${contentLength} bytes`)
          const buffer = await response.arrayBuffer()
          logDebug(`图片数据已读取: ${buffer.byteLength} bytes`)
          data = buffer
        } else {
          data = await response.text()
          logDebug(`文本响应`, data)
        }

        logInfo(`API请求成功: ${method} ${endpoint}`)
        return data
      } catch (error: any) {
        lastError = error
        const errorMsg = error?.message || String(error)
        logWarn(`API请求失败 (尝试 ${attempt}/${retryAttempts}): ${errorMsg}`)

        if (attempt < retryAttempts) {
          const delay = retryDelay * attempt
          logDebug(`等待 ${delay}ms 后重试...`)
          await new Promise(resolve => setTimeout(resolve, delay))
        }
      }
    }

    logError(`API请求最终失败: ${method} ${endpoint}`, lastError)
    throw lastError
  }

  /**
   * 保存图片到本地
   */
  async function saveImageLocally(imageData: ArrayBuffer, taskId: number): Promise<string | null> {
    try {
      const tempDir = path.join(process.cwd(), 'temp_images')
      
      // 确保目录存在
      if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir, { recursive: true })
      }
      
      const imagePath = path.join(tempDir, `task_${taskId}_${Date.now()}.png`)
      fs.writeFileSync(imagePath, Buffer.from(imageData))
      logInfo(`图片已保存到本地`, { path: imagePath })
      return imagePath
    } catch (error: any) {
      logError(`保存图片失败`, error)
      return null
    }
  }

  /**
   * 指令：测试API连接
   */
  ctx.command('steamdt', 'SteamDT客户端')
    .subcommand('test', '测试API连接')
    .action(async ({ session }) => {
      try {
        logInfo('开始测试API连接')
        const result = (await fetchAPI('/health')) as HealthStatus

        let message = '✅ API连接测试成功\n'
        message += `━━━━━━━━━━━━━━━━━━━━━━\n`
        message += `API地址: ${apiUrl}\n`
        message += `服务状态: ${result.status === 'healthy' ? '✅ 健康' : '❌ 异常'}\n`
        message += `队列长度: ${result.queue_length}\n`
        message += `已完成任务: ${result.completed_tasks}\n`
        message += `时间戳: ${result.timestamp}\n`

        logInfo('API连接测试完成', result)
        return message
      } catch (error: any) {
        logError('API连接测试失败', error)
        return `❌ API连接失败\n地址: ${apiUrl}\n错误: ${error?.message || String(error)}`
      }
    })

  /**
   * 指令：添加爬取任务
   */
  ctx.command('scrape [scrolls:number] [priority:number]', '添加爬取任务')
    .option('scrolls', '-s <scrolls:number> 滚动次数，默认5')
    .option('priority', '-p <priority:number> 优先级，默认0')
    .action(async ({ session }, scrolls, priority) => {
      try {
        scrolls = scrolls ?? 5
        priority = priority ?? 0

        logInfo(`添加任务`, { scrolls, priority })

        if (scrolls < 1 || scrolls > 100) {
          logWarn(`参数验证失败: scrolls=${scrolls}`)
          return '❌ 滚动次数必须在1-100之间'
        }

        if (priority < 0 || priority > 10) {
          logWarn(`参数验证失败: priority=${priority}`)
          return '❌ 优先级必须在0-10之间'
        }

        // 发送初始消息
        if (session) {
          await session.send('⏳ 正在添加任务到队列...')
        }

        const result = (await fetchAPI('/api/scrape', 'POST', {
          scrolls,
          priority,
        })) as any

        const taskId = result.task_id
        logInfo(`任务已添加`, { task_id: taskId, scrolls, priority })

        let message = `✅ 任务已添加到队列\n`
        message += `📊 滚动次数: ${scrolls}\n`
        message += `⚡ 优先级: ${priority}\n`
        message += `🕐 创建时间: ${result.created_at}\n`
        message += `📍 任务ID: ${taskId}\n`
        message += `📋 队列长度: ${result.queue_length}`

        // 发送任务信息
        if (session) {
          await session.send(message)
          await session.send('⏳ 正在处理任务，请稍候...')
        }

        // 轮询等待任务完成（最多等待10分钟）
        let completed = false
        let attempts = 0
        const maxAttempts = 600
        let lastStatus = 'queued'

        while (!completed && attempts < maxAttempts) {
          await new Promise(resolve => setTimeout(resolve, 1000))
          attempts++

          try {
            const taskResult = (await fetchAPI(`/api/task/${taskId}`)) as any
            
            // 状态变化时发送消息
            if (taskResult.status !== lastStatus) {
              lastStatus = taskResult.status
              if (taskResult.status === 'processing') {
                if (session) {
                  await session.send('⚙️ 任务正在处理中...')
                }
              }
            }
            
            if (taskResult.status === 'completed') {
              completed = true
              logInfo(`任务已完成`, { task_id: taskId })
              
              message = `✅ 任务完成！\n`
              
              if (taskResult.result) {
                message += `📈 统计数据:\n`
                message += `  上升: ${taskResult.result.up_count}\n`
                message += `  下降: ${taskResult.result.down_count}\n`
                message += `  总计: ${taskResult.result.total_count}\n`
                message += `  平均上升: ${taskResult.result.avg_up_percent}%\n`
                message += `  平均下降: ${taskResult.result.avg_down_percent}%\n`
              }

              if (session) {
                await session.send(message)
                await session.send('📥 正在获取图片...')
              }

              // 获取并保存图片到本地
              try {
                logInfo(`获取任务图片`, { task_id: taskId })
                const imageData = await fetchAPI(`/api/task/${taskId}/image`)
                
                if (imageData instanceof ArrayBuffer) {
                  const imagePath = await saveImageLocally(imageData, taskId)
                  
                  if (imagePath && session) {
                    await session.send(`<image url="file://${imagePath}" />`)
                    logInfo(`任务图片已发送`, { task_id: taskId, path: imagePath })
                  }
                }
              } catch (imgError: any) {
                logWarn(`获取或保存图片失败`, imgError)
                if (session) {
                  await session.send(`⚠️ 获取图片失败: ${imgError?.message || String(imgError)}`)
                }
              }
            } else if (taskResult.status === 'failed') {
              completed = true
              logError(`任务失败`, { task_id: taskId, error: taskResult.error })
              if (session) {
                await session.send(`❌ 任务失败: ${taskResult.error}`)
              }
            }
          } catch (pollError: any) {
            logDebug(`轮询检查失败`, pollError)
          }
        }

        if (!completed) {
          const msg = `⚠️ 任务仍在处理中，请稍后使用 /task ${taskId} 查询结果`
          if (session) {
            await session.send(msg)
          }
          return msg
        }

        return ''
      } catch (error: any) {
        logError(`添加任务失败`, error)
        const msg = `❌ 添加任务失败: ${error?.message || String(error)}`
        if (session) {
          await session.send(msg)
        }
        return msg
      }
    })

  /**
   * 指令：查看队列状态
   */
  ctx.command('queue', '查看队列状态').action(async ({ session }) => {
    try {
      logInfo('查询队列状态')
      const result = (await fetchAPI('/api/queue')) as QueueStatus

      let message = '📋 队列状态\n'
      message += `━━━━━━━━━━━━━━━━━━━━━━\n`
      message += `队列长度: ${result.queue_length}\n`
      message += `已完成任务: ${result.completed_count}\n`

      if (result.current_task) {
        message += `\n⏳ 当前任务:\n`
        message += `  滚动次数: ${result.current_task.scrolls}\n`
        message += `  优先级: ${result.current_task.priority}\n`
        message += `  创建时间: ${result.current_task.created_at}\n`
      }

      if (result.queue.length > 0) {
        message += `\n📝 队列中的任务:\n`
        result.queue.slice(0, 5).forEach((task, idx) => {
          message += `  ${idx + 1}. 滚动: ${task.scrolls}, 优先级: ${task.priority}\n`
        })
        if (result.queue.length > 5) {
          message += `  ... 还有 ${result.queue.length - 5} 个任务\n`
        }
      }

      logInfo('队列状态查询完成', { queue_length: result.queue_length, completed_count: result.completed_count })
      return message
    } catch (error: any) {
      logError('队列状态查询失败', error)
      return `❌ 查询队列失败: ${error?.message || String(error)}`
    }
  })

  /**
   * 指令：查看任务结果
   */
  ctx.command('task [task_id:number]', '查看任务结果').action(async ({ session }, task_id) => {
    try {
      if (task_id === undefined) {
        return '❌ 请指定任务ID，用法: /task <task_id>'
      }

      logInfo(`查询任务结果`, { task_id })
      const result = (await fetchAPI(`/api/task/${task_id}`)) as TaskResult

      let message = `📊 任务结果 #${task_id}\n`
      message += `━━━━━━━━━━━━━━━━━━━━━━\n`
      message += `状态: ${result.status}\n`
      message += `滚动次数: ${result.scrolls}\n`
      message += `优先级: ${result.priority}\n`
      message += `创建时间: ${result.created_at}\n`

      if (result.started_at) {
        message += `开始时间: ${result.started_at}\n`
      }

      if (result.completed_at) {
        message += `完成时间: ${result.completed_at}\n`
      }

      if (result.result) {
        message += `\n📈 统计数据:\n`
        message += `  上升: ${result.result.up_count}\n`
        message += `  下降: ${result.result.down_count}\n`
        message += `  总计: ${result.result.total_count}\n`
        message += `  平均上升: ${result.result.avg_up_percent}%\n`
        message += `  平均下降: ${result.result.avg_down_percent}%\n`
      }

      if (result.error) {
        message += `\n❌ 错误: ${result.error}\n`
      }

      logInfo('任务结果查询完成', { task_id, status: result.status })
      return message
    } catch (error: any) {
      logError('任务结果查询失败', error)
      return `❌ 查询任务失败: ${error?.message || String(error)}`
    }
  })

  /**
   * 指令：获取任务图片
   */
  ctx.command('image [task_id:number]', '获取任务图片').action(async ({ session }, task_id) => {
    try {
      if (task_id === undefined) {
        return '❌ 请指定任务ID，用法: /image <task_id>'
      }

      logInfo(`获取任务图片`, { task_id })
      const result = await fetchAPI(`/api/task/${task_id}/image`)

      if (result instanceof ArrayBuffer) {
        const imagePath = await saveImageLocally(result, task_id)
        
        if (imagePath && session) {
          await session.send(`<image url="file://${imagePath}" />`)
          logInfo('任务图片已获取并发送', { task_id, path: imagePath })
        }
        return ''
      } else {
        logError('响应不是图片数据', { task_id })
        return '❌ 获取图片失败'
      }
    } catch (error: any) {
      logError('获取任务图片失败', error)
      return `❌ 获取任务图片失败: ${error?.message || String(error)}`
    }
  })

  /**
   * 指令：健康检查
   */
  ctx.command('health', '健康检查').action(async ({ session }) => {
    try {
      logInfo('执行健康检查')
      const result = (await fetchAPI('/health')) as HealthStatus

      let message = '🏥 服务健康检查\n'
      message += `━━━━━━━━━━━━━━━━━━━━━━\n`
      message += `状态: ${result.status === 'healthy' ? '✅ 健康' : '❌ 异常'}\n`
      message += `队列长度: ${result.queue_length}\n`
      message += `已完成任务: ${result.completed_tasks}\n`
      message += `时间戳: ${result.timestamp}\n`

      logInfo(`服务状态: ${result.status}`)
      return message
    } catch (error: any) {
      logError(`健康检查失败`, error)
      return `❌ 健康检查失败: ${error?.message || String(error)}`
    }
  })

  /**
   * 指令：帮助信息
   */
  ctx.command('steamdt', 'SteamDT客户端')
    .subcommand('help', '显示帮助信息')
    .action(async ({ session }) => {
      logInfo('显示帮助信息')
      return usage
    })

  logInfo('SteamDT客户端初始化完成')
}
