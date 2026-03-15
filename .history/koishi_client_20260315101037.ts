import { Context, Schema, Logger } from 'koishi'

export const name = 'steamdt-client'
export const usage = `
SteamDT 异动数据爬虫客户端

支持的指令：
- /scrape [scrolls] [priority] - 添加爬取任务
- /queue - 查看队列状态
- /task [index] - 查看任务结果
- /image [index] - 获取任务图片
- /health - 健康检查
`

export interface Config {
  apiUrl: string
  timeout: number
}

export const Config: Schema<Config> = Schema.object({
  apiUrl: Schema.string().default('http://127.0.0.1:1145').description('API服务地址'),
  timeout: Schema.number().default(30000).description('请求超时时间（毫秒）'),
})

const logger = new Logger('steamdt-client')

export function apply(ctx: Context, config: Config) {
  const apiUrl = config.apiUrl.replace(/\/$/, '')
  const timeout = config.timeout

  /**
   * 发送HTTP请求的辅助函数
   */
  async function fetchAPI(endpoint: string, method: string = 'GET', body?: any) {
    try {
      const url = `${apiUrl}${endpoint}`
      const options: any = {
        method,
        timeout,
        headers: {
          'Content-Type': 'application/json',
        },
      }

      if (body) {
        options.body = JSON.stringify(body)
      }

      const response = await fetch(url, options)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const contentType = response.headers.get('content-type')
      if (contentType?.includes('application/json')) {
        return await response.json()
      } else if (contentType?.includes('image')) {
        return response
      } else {
        return await response.text()
      }
    } catch (error: any) {
      logger.error(`API请求失败: ${error?.message || String(error)}`)
      throw error
    }
  }

  /**
   * 指令：添加爬取任务
   * 用法: /scrape [scrolls] [priority]
   */
  ctx.command('scrape [scrolls:number] [priority:number]', '添加爬取任务')
    .option('scrolls', '-s <scrolls:number> ���动次数，默认5')
    .option('priority', '-p <priority:number> 优先级，默认0')
    .action(async ({ session }, scrolls, priority) => {
      try {
        scrolls = scrolls ?? 5
        priority = priority ?? 0

        if (scrolls < 1 || scrolls > 100) {
          return '❌ 滚动次数必须在1-100之间'
        }

        if (priority < 0 || priority > 10) {
          return '❌ 优先级必须在0-10之间'
        }

        const result = await fetchAPI('/api/scrape', 'POST', {
          scrolls,
          priority,
        })

        return `✅ 任务已添加到队列
📊 滚动次数: ${scrolls}
⚡ 优先级: ${priority}
🕐 创建时间: ${result.created_at}
📍 任务ID: ${result.task_id || '待分配'}`
      } catch (error: any) {
        return `❌ 添加任务失败: ${error?.message || String(error)}`
      }
    })

  /**
   * 指令：查看队列状态
   * 用法: /queue
   */
  ctx.command('queue', '查看队列状态').action(async ({ session }) => {
    try {
      const result = await fetchAPI('/api/queue')

      let message = '📋 队列状态\n'
      message += `━━━━━━━━━━━━━━━━━━━━━━\n`
      message += `⏳ 队列长度: ${result.queue_length}\n`
      message += `✅ 已完成任务: ${result.completed_count}\n`

      if (result.current_task) {
        message += `\n🔄 当前任务:\n`
        message += `  • 滚动次数: ${result.current_task.scrolls}\n`
        message += `  • 优先级: ${result.current_task.priority}\n`
        message += `  • 状态: ${result.current_task.status}\n`
      }

      if (result.queue && result.queue.length > 0) {
        message += `\n📝 等待队列 (前5个):\n`
        result.queue.slice(0, 5).forEach((task: any, index: number) => {
          message += `  ${index + 1}. scrolls=${task.scrolls}, priority=${task.priority}\n`
        })
        if (result.queue.length > 5) {
          message += `  ... 还有 ${result.queue.length - 5} 个任务\n`
        }
      }

      return message
    } catch (error: any) {
      return `❌ 获取队列状态失败: ${error?.message || String(error)}`
    }
  })

  /**
   * 指令：查看任务结果
   * 用法: /task [index]
   */
  ctx.command('task <index:number>', '查看任务结果')
    .action(async ({ session }, index) => {
      try {
        if (index < 0) {
          return '❌ 任务索引必须为非负数'
        }

        const result = await fetchAPI(`/api/task/${index}`)

        let message = `📊 任务 #${index} 结果\n`
        message += `━━━━━━━━━━━━━━━━━━━━━━\n`
        message += `状态: ${result.status}\n`
        message += `滚动次数: ${result.scrolls}\n`
        message += `优先级: ${result.priority}\n`
        message += `创建时间: ${result.created_at}\n`

        if (result.status === 'completed') {
          message += `完成时间: ${result.completed_at}\n`
          if (result.result) {
            message += `\n📈 统计数据:\n`
            message += `  • 上涨: ${result.result.up_count}\n`
            message += `  • 下跌: ${result.result.down_count}\n`
            message += `  • 总数: ${result.result.total_count}\n`
            message += `  • 平均涨幅: ${result.result.avg_up_percent?.toFixed(2)}%\n`
            message += `  • 平均跌幅: ${result.result.avg_down_percent?.toFixed(2)}%\n`
            message += `  • 图片: ${result.result.image_path}\n`
          }
        } else if (result.status === 'failed') {
          message += `错误: ${result.error}\n`
        }

        return message
      } catch (error: any) {
        return `❌ 获取任务结果失败: ${error?.message || String(error)}`
      }
    })

  /**
   * 指令：获取任务图片
   * 用法: /image [index]
   */
  ctx.command('image <index:number>', '获取任务图片')
    .action(async ({ session }, index) => {
      try {
        if (index < 0) {
          return '❌ 任务索引必须为非负数'
        }

        const response = await fetchAPI(`/api/task/${index}/image`)

        if (response instanceof Response) {
          const buffer = await response.arrayBuffer()
          const base64 = Buffer.from(buffer).toString('base64')
          return `<image url="data:image/png;base64,${base64}" />`
        } else {
          return '❌ 获取图片失败'
        }
      } catch (error: any) {
        return `❌ 获取任务图片失败: ${error?.message || String(error)}`
      }
    })

  /**
   * 指令：健康检查
   * 用法: /health
   */
  ctx.command('health', '健康检查').action(async ({ session }) => {
    try {
      const result = await fetchAPI('/health')

      let message = '🏥 服务健康检查\n'
      message += `━━━━━━━━━━━━━━━━━━━━━━\n`
      message += `状态: ${result.status === 'healthy' ? '✅ 健康' : '❌ 异常'}\n`
      message += `队列长度: ${result.queue_length}\n`
      message += `已完成任务: ${result.completed_tasks}\n`
      message += `时间戳: ${result.timestamp}\n`

      return message
    } catch (error: any) {
      return `❌ 健康检查失败: ${error?.message || String(error)}`
    }
  })

  /**
   * 指令：帮助信息
   * 用法: /steamdt help
   */
  ctx.command('steamdt', 'SteamDT客户端')
    .subcommand('help', '显示帮助信息')
    .action(async ({ session }) => {
      return usage
    })

  logger.info('SteamDT客户端已加载')
  logger.info(`API服务地址: ${apiUrl}`)
}
