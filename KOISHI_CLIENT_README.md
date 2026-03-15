# SteamDT Koishi 客户端

这是一个为SteamDT同步版本API服务设计的Koishi框架客户端插件。每个API端点都对应一个指令。

## 功能特性

- ✅ 添加爬取任务到队列
- ✅ 查看队列状态
- ✅ 查看任务结果和统计数据
- ✅ 获取任务生成的表格图片
- ✅ 服务健康检查
- ✅ 完整的错误处理和日志记录

## 安装

### 前置要求

- Node.js >= 16
- Koishi >= 4.0.0

### 安装步骤

1. 将此插件放入Koishi的插件目录
2. 安装依赖：
```bash
npm install
```

3. 编译TypeScript：
```bash
npm run build
```

4. 在Koishi配置中启用此插件

## 配置

在Koishi配置文件中添加：

```yaml
plugins:
  steamdt-client:
    apiUrl: http://127.0.0.1:1145
    timeout: 30000
```

### 配置选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| apiUrl | string | http://127.0.0.1:1145 | API服务地址 |
| timeout | number | 30000 | 请求超时时间（毫秒） |

## 指令列表

### 1. `/scrape [scrolls] [priority]` - 添加爬取任务

添加一个新的爬取任务到队列。

**参数：**
- `scrolls` (可选): 滚动次数，范围1-100，默认5
- `priority` (可选): 优先级，范围0-10，默认0

**示例：**
```
/scrape 10 5
/scrape -s 20 -p 8
```

**返回示例：**
```
✅ 任务已添加到队列
📊 滚动次数: 10
⚡ 优先级: 5
🕐 创建时间: 2026-03-15T02:10:00.000Z
📍 任务ID: 待分配
```

### 2. `/queue` - 查看队列状态

查看当前队列的状态，包括队列长度、当前任务和等待中的任务。

**示例：**
```
/queue
```

**返回示例：**
```
📋 队列状态
━━━━━━━━━━━━━━━━━━━━━━
⏳ 队列长度: 3
✅ 已完成任务: 5

🔄 当前任务:
  • 滚动次数: 10
  • 优先级: 5
  • 状态: processing

📝 等待队列 (前5个):
  1. scrolls=5, priority=0
  2. scrolls=8, priority=2
  3. scrolls=15, priority=1
```

### 3. `/task <index>` - 查看任务结果

查看指定任务的详细结果和统计数据。

**参数：**
- `index` (必需): 任务索引号

**示例：**
```
/task 0
/task 5
```

**返回示例：**
```
📊 任务 #0 结果
━━━━━━━━━━━━━━━━━━━━━━
状态: completed
滚动次数: 10
优先级: 5
创建时间: 2026-03-15T02:10:00.000Z
完成时间: 2026-03-15T02:15:30.000Z

📈 统计数据:
  • 上涨: 45
  • 下跌: 32
  • 总数: 77
  • 平均涨幅: 3.45%
  • 平均跌幅: -2.12%
  • 图片: temp_table_1234567890.png
```

### 4. `/image <index>` - 获取任务图片

获取指定任务生成的表格图片。

**参数：**
- `index` (必需): 任务索引号

**示例：**
```
/image 0
/image 5
```

**返回：** 返回PNG格式的表格图片

### 5. `/health` - 健康检查

检查API服务的健康状态。

**示例：**
```
/health
```

**返回示例：**
```
🏥 服务健康检查
━━━━━━━━━━━━━━━━━━━━━━
状态: ✅ 健康
队列长度: 2
已完成任务: 10
时间戳: 2026-03-15T02:10:00.000Z
```

### 6. `/steamdt help` - 帮助信息

显示所有可用指令的帮助信息。

**示例：**
```
/steamdt help
```

## API端点映射

| 指令 | HTTP方法 | API端点 | 说明 |
|------|---------|---------|------|
| /scrape | POST | /api/scrape | 添加爬取任务 |
| /queue | GET | /api/queue | 获取队列状态 |
| /task | GET | /api/task/{index} | 获取任务结果 |
| /image | GET | /api/task/{index}/image | 获取任务图片 |
| /health | GET | /health | 健康检查 |

## 开发

### 构建

```bash
npm run build
```

### 监视模式

```bash
npm run dev
```

### 项目结构

```
.
├── koishi_client.ts      # 主插件文件
├── package.json          # 项目配置
├── tsconfig.json         # TypeScript配置
├── dist/                 # 编译输出目录
└── README.md             # 本文件
```

## 错误处理

所有指令都包含完整的错误处理。如果请求失败，会返回错误信息：

```
❌ 添加任务失败: Connection refused
❌ 获取队列状态失败: Timeout
❌ 获取任务结果失败: Task not found
```

## 日志

插件使用Koishi的日志系统，日志标签为 `steamdt-client`。

启动时会输出：
```
[steamdt-client] SteamDT客户端已加载
[steamdt-client] API服务地址: http://127.0.0.1:1145
```

## 许可证

MIT

## 相关项目

- [SteamDT API 服务](../api_server.py) - 同步版本API服务
- [Koishi](https://koishi.chat/) - 机器人框架
