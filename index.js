"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Config = exports.usage = exports.name = void 0;
exports.apply = apply;
const koishi_1 = require("koishi");
exports.name = 'steamdt-client';
exports.usage = `
SteamDT 异动数据爬虫客户端

支持的指令：
- /scrape [scrolls] [priority] - 添加爬取任务
- /queue - 查看队列状态
- /task [index] - 查看任务结果
- /image [index] - 获取任务图片
- /health - 健康检查
- /steamdt test - 测试API连接
`;
exports.Config = koishi_1.Schema.object({
    apiUrl: koishi_1.Schema.string()
        .default('http://127.0.0.1:1145')
        .description('API服务地址（如 http://127.0.0.1:1145）')
        .role('url'),
    timeout: koishi_1.Schema.number()
        .default(30000)
        .min(1000)
        .max(300000)
        .description('请求超时时间（毫秒，1000-300000）'),
    retryAttempts: koishi_1.Schema.number()
        .default(3)
        .min(0)
        .max(10)
        .description('网络失败重试次数（0-10）'),
    retryDelay: koishi_1.Schema.number()
        .default(1000)
        .min(100)
        .max(10000)
        .description('重试延迟时间（毫秒，100-10000）'),
    enableDetailedLogging: koishi_1.Schema.boolean()
        .default(false)
        .description('启用详细日志（用于调试）'),
}).description('基础配置');
const logger = new koishi_1.Logger('steamdt-client');
function apply(ctx, config) {
    const apiUrl = config.apiUrl.replace(/\/$/, '');
    const timeout = config.timeout;
    const retryAttempts = config.retryAttempts;
    const retryDelay = config.retryDelay;
    const enableDetailedLogging = config.enableDetailedLogging;
    logger.info(`SteamDT客户端已加载，API地址: ${apiUrl}，重试次数: ${retryAttempts}，超时: ${timeout}ms`);
    /**
     * 日志辅助函数
     */
    function logDebug(message, data) {
        if (enableDetailedLogging) {
            logger.debug(`[DEBUG] ${message}${data ? ': ' + JSON.stringify(data) : ''}`);
        }
    }
    function logInfo(message, data) {
        logger.info(`[INFO] ${message}${data ? ': ' + JSON.stringify(data) : ''}`);
    }
    function logWarn(message, data) {
        logger.warn(`[WARN] ${message}${data ? ': ' + JSON.stringify(data) : ''}`);
    }
    function logError(message, error) {
        const errorMsg = error?.message || String(error);
        logger.error(`[ERROR] ${message}: ${errorMsg}`);
        if (enableDetailedLogging && error?.stack) {
            logger.debug(`[STACK] ${error.stack}`);
        }
    }
    /**
     * 发送HTTP请求的辅助函数（带重试机制）
     */
    async function fetchAPI(endpoint, method = 'GET', body) {
        let lastError = null;
        for (let attempt = 1; attempt <= retryAttempts; attempt++) {
            try {
                const url = `${apiUrl}${endpoint}`;
                logDebug(`[${method}] ${url} (尝试 ${attempt}/${retryAttempts})`);
                const options = {
                    method,
                    timeout,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                };
                if (body) {
                    options.body = JSON.stringify(body);
                    logDebug(`请求体`, body);
                }
                const startTime = Date.now();
                const response = await fetch(url, options);
                const duration = Date.now() - startTime;
                logDebug(`响应状态: ${response.status}，耗时: ${duration}ms`);
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`);
                }
                const contentType = response.headers.get('content-type');
                let data;
                if (contentType?.includes('application/json')) {
                    data = await response.json();
                    logDebug(`JSON响应`, data);
                }
                else if (contentType?.includes('image')) {
                    const contentLength = response.headers.get('content-length');
                    logDebug(`收到图片数据，大小: ${contentLength} bytes`);
                    const buffer = await response.arrayBuffer();
                    logDebug(`图片数据已读取: ${buffer.byteLength} bytes`);
                    data = buffer;
                }
                else {
                    data = await response.text();
                    logDebug(`文本响应`, data);
                }
                logInfo(`API请求成功: ${method} ${endpoint}`);
                return data;
            }
            catch (error) {
                lastError = error;
                const errorMsg = error?.message || String(error);
                logWarn(`API请求失败 (尝试 ${attempt}/${retryAttempts}): ${errorMsg}`);
                if (attempt < retryAttempts) {
                    const delay = retryDelay * attempt;
                    logDebug(`等待 ${delay}ms 后重试...`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
        }
        logError(`API请求最终失败: ${method} ${endpoint}`, lastError);
        throw lastError;
    }
    /**
     * 指令：测试API连接
     * 用法: /steamdt test
     */
    ctx.command('steamdt', 'SteamDT客户端')
        .subcommand('test', '测试API连接')
        .action(async ({ session }) => {
        try {
            logInfo('开始测试API连接');
            const result = (await fetchAPI('/health'));
            let message = '✅ API连接测试成功\n';
            message += `━━━━━━━━━━━━━━━━━━━━━━\n`;
            message += `API地址: ${apiUrl}\n`;
            message += `服务状态: ${result.status === 'healthy' ? '✅ 健康' : '❌ 异常'}\n`;
            message += `队列长度: ${result.queue_length}\n`;
            message += `已完成任务: ${result.completed_tasks}\n`;
            message += `时间戳: ${result.timestamp}\n`;
            logInfo('API连接测试完成', result);
            return message;
        }
        catch (error) {
            logError('API连接测试失败', error);
            return `❌ API连接失败\n地址: ${apiUrl}\n错误: ${error?.message || String(error)}`;
        }
    });
    /**
     * 指令：添加爬取任务
     * 用法: /scrape [scrolls] [priority]
     */
    ctx.command('scrape [scrolls:number] [priority:number]', '添加爬取任务')
        .option('scrolls', '-s <scrolls:number> 滚动次数，默认5')
        .option('priority', '-p <priority:number> 优先级，默认0')
        .action(async ({ session }, scrolls, priority) => {
        try {
            scrolls = scrolls ?? 5;
            priority = priority ?? 0;
            logInfo(`添加任务`, { scrolls, priority });
            if (scrolls < 1 || scrolls > 100) {
                logWarn(`参数验证失败: scrolls=${scrolls}`);
                return '❌ 滚动次数必须在1-100之间';
            }
            if (priority < 0 || priority > 10) {
                logWarn(`参数验证失败: priority=${priority}`);
                return '❌ 优先级必须在0-10之间';
            }
            const result = (await fetchAPI('/api/scrape', 'POST', {
                scrolls,
                priority,
            }));
            const taskIndex = result.task_index ?? result.index ?? 0;
            logInfo(`任务已添加`, { task_index: taskIndex, scrolls, priority });
            let message = `✅ 任务已添加到队列
📊 滚动次数: ${scrolls}
⚡ 优先级: ${priority}
🕐 创建时间: ${result.created_at}
📍 任务ID: ${taskIndex}`;
            // 轮询等待任务完成（最多等待5分钟）
            message += `\n⏳ 等待任务完成...`;
            let completed = false;
            let attempts = 0;
            const maxAttempts = 300; // 5分钟，每秒检查一次
            while (!completed && attempts < maxAttempts) {
                await new Promise(resolve => setTimeout(resolve, 1000));
                attempts++;
                try {
                    const taskResult = (await fetchAPI(`/api/task/${taskIndex}`));
                    if (taskResult.status === 'completed') {
                        completed = true;
                        logInfo(`任务已完成`, { task_index: taskIndex });
                        message += `\n✅ 任务完成！\n`;
                        if (taskResult.result) {
                            message += `📈 统计数据:\n`;
                            message += `  上升: ${taskResult.result.up_count}\n`;
                            message += `  下降: ${taskResult.result.down_count}\n`;
                            message += `  总计: ${taskResult.result.total_count}\n`;
                            message += `  平均上升: ${taskResult.result.avg_up_percent}%\n`;
                            message += `  平均下降: ${taskResult.result.avg_down_percent}%\n`;
                        }
                        // 自动获取并显示图片
                        try {
                            logInfo(`自动获取任务图片`, { task_index: taskIndex });
                            const imageData = await fetchAPI(`/api/task/${taskIndex}/image`);
                            if (imageData instanceof ArrayBuffer && session) {
                                const blob = new Blob([imageData], { type: 'image/png' });
                                const url = URL.createObjectURL(blob);
                                await session.send(`<image url="${url}" />`);
                                logInfo(`任务图片已发送`, { task_index: taskIndex });
                            }
                        }
                        catch (imgError) {
                            logWarn(`自动获取图片失败`, imgError);
                        }
                    }
                    else if (taskResult.status === 'failed') {
                        completed = true;
                        logError(`任务失败`, { task_index: taskIndex, error: taskResult.error });
                        message += `\n❌ 任务失败: ${taskResult.error}`;
                    }
                }
                catch (pollError) {
                    logDebug(`轮询检查失败`, pollError);
                }
            }
            if (!completed) {
                message += `\n⚠️ 任务仍在处理中，请稍后使用 /task ${taskIndex} 查询结果`;
            }
            return message;
        }
        catch (error) {
            logError(`添加任务失败`, error);
            return `❌ 添加任务失败: ${error?.message || String(error)}`;
        }
    });
    /**
     * 指令：查看队列状态
     * 用法: /queue
     */
    ctx.command('queue', '查看队列状态').action(async ({ session }) => {
        try {
            logInfo('查询队列状态');
            const result = (await fetchAPI('/api/queue'));
            let message = '📋 队列状态\n';
            message += `━━━━━━━━━━━━━━━━━━━━━━\n`;
            message += `队列长度: ${result.queue_length}\n`;
            message += `已完成任务: ${result.completed_count}\n`;
            if (result.current_task) {
                message += `\n⏳ 当前任务:\n`;
                message += `  滚动次数: ${result.current_task.scrolls}\n`;
                message += `  优先级: ${result.current_task.priority}\n`;
                message += `  创建时间: ${result.current_task.created_at}\n`;
            }
            if (result.queue.length > 0) {
                message += `\n📝 队列中的任务:\n`;
                result.queue.slice(0, 5).forEach((task, idx) => {
                    message += `  ${idx + 1}. 滚动: ${task.scrolls}, 优先级: ${task.priority}\n`;
                });
                if (result.queue.length > 5) {
                    message += `  ... 还有 ${result.queue.length - 5} 个任务\n`;
                }
            }
            logInfo('队列状态查询完成', { queue_length: result.queue_length, completed_count: result.completed_count });
            return message;
        }
        catch (error) {
            logError('队列状态查询失败', error);
            return `❌ 查询队列失败: ${error?.message || String(error)}`;
        }
    });
    /**
     * 指令：查看任务结果
     * 用法: /task [index]
     */
    ctx.command('task [index:number]', '查看任务结果').action(async ({ session }, index) => {
        try {
            if (index === undefined) {
                return '❌ 请指定任务索引，用法: /task <index>';
            }
            logInfo(`查询任务结果`, { index });
            const result = (await fetchAPI(`/api/task/${index}`));
            let message = `📊 任务结果 #${index}\n`;
            message += `━━━━━━━━━━━━━━━━━━━━━━\n`;
            message += `状态: ${result.status}\n`;
            message += `滚动次数: ${result.scrolls}\n`;
            message += `优先级: ${result.priority}\n`;
            message += `创建时间: ${result.created_at}\n`;
            if (result.completed_at) {
                message += `完成时间: ${result.completed_at}\n`;
            }
            if (result.result) {
                message += `\n📈 统计数据:\n`;
                message += `  上升: ${result.result.up_count}\n`;
                message += `  下降: ${result.result.down_count}\n`;
                message += `  总计: ${result.result.total_count}\n`;
                message += `  平均上升: ${result.result.avg_up_percent}%\n`;
                message += `  平均下降: ${result.result.avg_down_percent}%\n`;
            }
            if (result.error) {
                message += `\n❌ 错误: ${result.error}\n`;
            }
            logInfo('任务结果查询完成', { index, status: result.status });
            return message;
        }
        catch (error) {
            logError('任务结果查询失败', error);
            return `❌ 查询任务失败: ${error?.message || String(error)}`;
        }
    });
    /**
     * 指令：获取任务图片
     * 用法: /image [index]
     */
    ctx.command('image [index:number]', '获取任务图片').action(async ({ session }, index) => {
        try {
            if (index === undefined) {
                return '❌ 请指定任务索引，用法: /image <index>';
            }
            logInfo(`获取任务图片`, { index });
            const result = await fetchAPI(`/api/task/${index}/image`);
            if (result instanceof ArrayBuffer) {
                const blob = new Blob([result], { type: 'image/png' });
                const url = URL.createObjectURL(blob);
                logInfo('任务图片已获取', { index, size: result.byteLength });
                if (session) {
                    await session.send(`<image url="${url}" />`);
                }
                return '';
            }
            else {
                logError('响应不是图片数据', { index });
                return '❌ 获取图片失败';
            }
        }
        catch (error) {
            logError('获取任务图片失败', error);
            return `❌ 获取任务图片失败: ${error?.message || String(error)}`;
        }
    });
    /**
     * 指令：健康检查
     * 用法: /health
     */
    ctx.command('health', '健康检查').action(async ({ session }) => {
        try {
            logInfo('执行健康检查');
            const result = (await fetchAPI('/health'));
            let message = '🏥 服务健康检查\n';
            message += `━━━━━━━━━━━━━━━━━━━━━━\n`;
            message += `状态: ${result.status === 'healthy' ? '✅ 健康' : '❌ 异常'}\n`;
            message += `队列长度: ${result.queue_length}\n`;
            message += `已完成任务: ${result.completed_tasks}\n`;
            message += `时间戳: ${result.timestamp}\n`;
            logInfo(`服务状态: ${result.status}`);
            return message;
        }
        catch (error) {
            logError(`健康检查失败`, error);
            return `❌ 健康检查失败: ${error?.message || String(error)}`;
        }
    });
    /**
     * 指令：帮助信息
     * 用法: /steamdt help
     */
    ctx.command('steamdt', 'SteamDT客户端')
        .subcommand('help', '显示帮助信息')
        .action(async ({ session }) => {
        logInfo('显示帮助信息');
        return exports.usage;
    });
    logInfo('SteamDT客户端初始化完成');
}
//# sourceMappingURL=koishi_client.js.map