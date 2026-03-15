# SteamDT Koishi 客户端 - API映射文档

本文档详细说明每个Koishi指令如何映射到后端API端点。

## 指令与API映射表

| 指令 | HTTP方法 | API端点 | 功能 | 状态码 |
|------|---------|---------|------|--------|
| `/scrape` | POST | `/api/scrape` | 添加爬取任务 | 200 |
| `/queue` | GET | `/api/queue` | 获取队列状态 | 200 |
| `/task <index>` | GET | `/api/task/{index}` | 获取任务结果 | 200/400/404 |
| `/image <index>` | GET | `/api/task/{index}/image` | 获取任务图片 | 200/400/404 |
| `/health` | GET | `/health` | 健康检查 | 200 |

## 详细API说明

### 1. POST /api/scrape - 添加爬取任务

**Koishi指令：**
```
/scrape [scrolls] [priority]
```

**请求体：**
```json
{
  "scrolls": 10,
  "priority": 5
}
```

**响应（成功 200）：**
```json
{
  "scrolls": 10,
  "priority": 5,
  "created_at": "2026-03-15T02:10:00.000Z",
  "status": "queued",
  "task_id": "task_001"
}
```

**响应（失败 400）：**
```json
{
  "detail": "Invalid scrolls value"
}
```

**Koishi处理：**
- 验证参数范围（scrolls: 1-100, priority: 0-10）
- 发送POST请求到API
- 解析响应并格式化输出
- 显示任务创建成功信息

---

### 2. GET /api/queue - 获取队列状态

**Koishi指令：**
```
/queue
```

**请求参数：** 无

**响应（成功 200）：**
```json
{
  "queue_length": 3,
  "current_task": {
    "scrolls": 10,
    "priority": 5,
    "created_at": "2026-03-15T02:10:00.000Z",
    "status": "processing"
  },
  "completed_count": 5,
  "queue": [
    {
      "scrolls": 5,
      "priority": 0,
      "created_at": "2026-03-15T02:10:05.000Z",
      "status": "queued"
    },
    {
      "scrolls": 8,
      "priority": 2,
      "created_at": "2026-03-15T02:10:10.000Z",
      "status": "queued"
    }
  ]
}
```

**Koishi处理：**
- 发送GET请求到API
- 解析队列数据
- 格式化显示队列状态、当前任务和等待队列
- 最多显示前5个等待任务

---

### 3. GET /api/task/{index} - 获取任务结果

**Koishi指令：**
```
/task <index>
```

**请求参数：**
- `index` (必需): 任务索引号，非负整数

**响应（成功 200）：**
```json
{
  "scrolls": 10,
  "priority": 5,
  "created_at": "2026-03-15T02:10:00.000Z",
  "status": "completed",
  "completed_at": "2026-03-15T02:15:30.000Z",
  "result": {
    "up_count": 45,
    "down_count": 32,
    "total_count": 77,
    "avg_up_percent": 3.45,
    "avg_down_percent": -2.12,
    "image_path": "temp_table_1234567890.png"
  }
}
```

**响应（任务不存在 404）：**
```json
{
  "detail": "Task not found"
}
```

**响应（参数错误 400）：**
```json
{
  "detail": "Invalid task index"
}
```

**Koishi处理：**
- 验证index为非负数
- 发送GET请求到API
- 根据任务状态显示不同信息：
  - `completed`: 显示统计数据
  - `processing`: 显示处理中信息
  - `failed`: 显示错误信息
- 格式化输出结果

---

### 4. GET /api/task/{index}/image - 获取任务图片

**Koishi指令：**
```
/image <index>
```

**请求参数：**
- `index` (必需): 任务索引号，非负整数

**响应（成功 200）：**
- Content-Type: `image/png`
- Body: PNG图片二进制数据

**响应（任务未完成 400）：**
```json
{
  "detail": "Task not completed"
}
```

**响应（图片不存在 404）：**
```json
{
  "detail": "Image file not found"
}
```

**Koishi处理：**
- 验证index为非负数
- 发送GET请求到API
- 接收图片二进制数据
- 转换为Base64编码
- 以图片消息格式返回给用户

---

### 5. GET /health - 健康检查

**Koishi指令：**
```
/health
```

**请求参数：** 无

**响应（成功 200）：**
```json
{
  "status": "healthy",
  "queue_length": 2,
  "completed_tasks": 10,
  "timestamp": "2026-03-15T02:10:00.000Z"
}
```

**Koishi处理：**
- 发送GET请求到API
- 检查响应状态
- 显示服务健康状态、队列长度和已完成任务数

---

## 请求流程图

```
用户输入指令
    ↓
Koishi解析指令
    ↓
验证参数
    ↓
构建HTTP请求
    ↓
发送到API服务
    ↓
等待响应
    ↓
解析响应数据
    ↓
格式化输出
    ↓
返回给用户
```

## 错误处理流程

```
发送请求
    ↓
检查HTTP状态码
    ↓
├─ 2xx: 成功 → 解析数据 → 返回结果
├─ 4xx: 客户端错误 → 显示错误信息
├─ 5xx: 服务器错误 → 显示错误信息
└─ 网络错误 → 显示连接失败信息
```

## 参数验证规则

### /scrape 指令

| 参数 | 类型 | 范围 | 默认值 | 说明 |
|------|------|------|--------|------|
| scrolls | number | 1-100 | 5 | 滚动次数 |
| priority | number | 0-10 | 0 | 优先级 |

**验证逻辑：**
```typescript
if (scrolls < 1 || scrolls > 100) {
  return '❌ 滚动次数必须在1-100之间'
}
if (priority < 0 || priority > 10) {
  return '❌ 优先级必须在0-10之间'
}
```

### /task 和 /image 指令

| 参数 | 类型 | 范围 | 说明 |
|------|------|------|------|
| index | number | ≥ 0 | 任务索引 |

**验证逻辑：**
```typescript
if (index < 0) {
  return '❌ 任务索引必须为非负数'
}
```

## 超时配置

**默认超时时间：** 30000毫秒（30秒）

**可配置项：**
```yaml
plugins:
  steamdt-client:
    timeout: 30000  # 毫秒
```

**超时处理：**
- 如果请求超过配置时间，返回超时错误
- 用户可根据网络情况调整超时时间

## 响应格式标准化

### 成功响应

所有成功的Koishi指令返回格式化的文本消息，包含：
- 状态符号（✅ 或 📊 等）
- 关键信息
- 详细数据（如适用）

### 错误响应

所有错误返回格式：
```
❌ [操作名称]失败: [错误信息]
```

示例：
```
❌ 添加任务失败: Connection refused
❌ 获取队列状态失败: Timeout
❌ 获取任务结果失败: Task not found
```

## 数据转换

### 请求数据转换

```typescript
// Koishi参数 → API请求体
{
  scrolls: 10,
  priority: 5
}
```

### 响应数据转换

```typescript
// API响应 → Koishi消息
{
  up_count: 45,
  down_count: 32,
  avg_up_percent: 3.45
}
↓
"  • 上涨: 45\n  • 下跌: 32\n  • 平均涨幅: 3.45%"
```

## 并发处理

- 每个指令调用都是独立的HTTP请求
- 支持多个用户同时发送指令
- API服务使用任务队列处理并发请求
- Koishi客户端不限制并发数量

## 日志记录

所有API调用都会记录日志：

```
[steamdt-client] API请求: POST /api/scrape
[steamdt-client] 响应状态: 200
[steamdt-client] 响应时间: 125ms
```

错误日志：
```
[steamdt-client] API请求失败: GET /api/task/999
[steamdt-client] 错误信息: Task not found
```

## 性能指标

| 操作 | 平均响应时间 | 说明 |
|------|------------|------|
| /scrape | 50-100ms | 添加任务到队列 |
| /queue | 10-50ms | 查询队列状态 |
| /task | 20-100ms | 查询任务结果 |
| /image | 100-500ms | 获取图片（取决于图片大小） |
| /health | 5-20ms | 健康检查 |

## 兼容性

- **Koishi版本：** 4.0.0+
- **Node.js版本：** 16.0.0+
- **API服务版本：** 2.1.0+

## 相关文档

- [快速开始](QUICKSTART.md)
- [详细文档](KOISHI_CLIENT_README.md)
- [使用示例](EXAMPLES.md)
- [API文档](API_DOCS.md)
