import { Context, Schema, Logger } from 'koishi'
import axios from 'axios'

export const name = 'steamdt'
export const usage = `
SteamDT CS2 饰品异动数据查询插件

命令:
- steamdt.scrape [scrolls] [priority] - 添加爬取任务
- steamdt.queue - 查看队列状态
- steamdt.result [index] - 查看任务结果
- steamdt.image [index] - 获取表格图片
- steamdt.stats - 查看统计信息
`

export interface Config {
  apiUrl: string
  apiPort: number
  timeout: number
}

export const Config: Schema<Config> = Schema.object({
  apiUrl: Schema.string().default('127.0.0.1').description('API 服务地址'),
  apiPort: Schema.number().default(1145).description('API 服务端口'),
  timeout: Schema.number().default(30000).description('请求超时时间（毫秒）'),
})

const logger = new Logger('steamdt')

export function apply(ctx: Context, config: Config) {
  const baseUrl = `http://${config.apiUrl}:${config.apiPort}`
  const client = axios.create({
    baseURL: baseUrl,
    timeout: config.timeout,
  })

  // 添加爬取任务
  ctx.command('steamdt.scrape [scrolls:number] [priority:number]', '添加爬取任务')
    .option('scrolls', '-s <scrolls:number> 滑动次数（1-50）', { fallback: 10 })
    .option('priority', '-p <priority:number> 优先级', { fallback: 0 })
    .action(async ({ session }, scrolls, priority) => {
      try {
        if (scrolls < 1 || scrolls > 50) {
          return '滑动次数必须在 1-50 之间'
        }

        const response = await client.post('/api/scrape', null, {
          params: { scrolls, priority },
        })

        const data = response.data
        return `✓ 任务已添加到队列
滑动次数: ${data.scrolls}
优先级: ${data.priority}
队列位置: ${data.queue_position}
消息: ${data.message}`
      } catch (error) {
        logger.error('添加任务失败:', error)
        return `✗ 添加任务失败: ${error.message}`
      }
    })

  // 查看队列状态
  ctx.command('steamdt.queue', '查看队列状态')
    .action(async ({ session }) => {
      try {
        const response = await client.get('/api/queue')
        const data = response.data

        let message = `📊 队列状态
队列长度: ${data.queue_length}
已完成: ${data.completed_count}`

        if (data.current_task) {
          message += `
当前任务:
  滑动次数: ${data.current_task.scrolls}
  优先级: ${data.current_task.priority}`
        }

        if (data.queue.length > 0) {
          message += '\n\n等待中的任务:'
          data.queue.slice(0, 5).forEach((task, index) => {
            message += `\n  ${index + 1}. scrolls=${task.scrolls}, priority=${task.priority}`
          })
          if (data.queue.length > 5) {
            message += `\n  ... 还有 ${data.queue.length - 5} 个任务`
          }
        }

        return message
      } catch (error) {
        logger.error('获取队列状态失败:', error)
        return `✗ 获取队列状态失败: ${error.message}`
      }
    })

  // 查看任务结果
  ctx.command('steamdt.result <index:number>', '查看任务结果')
    .action(async ({ session }, index) => {
      try {
        const response = await client.get(`/api/task/${index}`)
        const data = response.data

        if (data.status === 'failed') {
          return `✗ 任务失败
错误: ${data.error}`
        }

        if (data.status !== 'completed') {
          return `⏳ 任务未完成
状态: ${data.status}`
        }

        const result = data.result
        return `✓ 任务完成
总条数: ${result.total}
上涨: ${result.up_count}
下跌: ${result.down_count}
平均涨幅: ${result.avg_change}%
创建时间: ${data.created_at}
完成时间: ${data.completed_at}`
      } catch (error) {
        logger.error('获取任务结果失败:', error)
        return `✗ 获取任务结果失败: ${error.message}`
      }
    })

  // 获取表格图片
  ctx.command('steamdt.image <index:number>', '获取表格图片')
    .action(async ({ session }, index) => {
      try {
        const response = await client.get(`/api/task/${index}/image`, {
          responseType: 'arraybuffer',
        })

        const imageBuffer = Buffer.from(response.data, 'binary')
        const base64 = imageBuffer.toString('base64')
        const imageUrl = `data:image/png;base64,${base64}`

        return session.send(`<image url="${imageUrl}" />`)
      } catch (error) {
        logger.error('获取表格图片失败:', error)
        return `✗ 获取表格图片失败: ${error.message}`
      }
    })

  // 查看统计信息
  ctx.command('steamdt.stats', '查看统计信息')
    .action(async ({ session }) => {
      try {
        const response = await client.get('/health')
        const data = response.data

        return `📈 服务状态
状态: ${data.status}
队列长度: ${data.queue_length}
已完成任务: ${data.completed_tasks}`
      } catch (error) {
        logger.error('获取统计信息失败:', error)
        return `✗ 获取统计信息失败: ${error.message}`
      }
    })

  logger.info('SteamDT 插件已加载')
}
