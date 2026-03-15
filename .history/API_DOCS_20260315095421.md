# SteamDT 异动数据 API 文档 - 任务队列版本

## 概述

这是一个支持**任务队列**和**优先级处理**的 RESTful API 服务。支持多个请求排队处理，按优先级执行。

## 快速开始

### 启动服务

```bash
python api_server.py 5000
```

服务将在 `http://127.0.0.1:5000` 启动

### 访问 API 文档

- **Swagger UI**: http://127.0.0.1:5000/docs
- **ReDoc**: http://127.0.0.1:5000/redoc

## API 端点

### 1. 添加任务到队列

**请求:**
```
POST /api/scrape?scrolls=10&priority=0
```

**参数:**
- `scrolls` (int): 滑动次数，范围 1-50（默认 10）
- `priority` (int): 优先级，值越大优先级越高（默认 0）

**响应:**
```json
{
  "status": "已添加到队列",
  "scrolls": 10,
  "priority": 0,
  "queue_position": 2,
  "message": "任务已添加到队列，当前队列长度: 2",
  "timestamp": "2026-03-15T01:53:55.000000"
}
```

### 2. 获取队列状态

**请求:**
```
GET /api/queue
```

**响应:**
```json
{
  "queue_length": 2,
  "current_task": {
    "scrolls": 10,
    "priority": 1,
    "created_at": "2026-03-15T01:53:50.000000",
    "status": "running"
  },
  "completed_count": 5,
  "queue": [
    {
      "scrolls": 10,
      "priority": 0,
      "created_at": "2026-03-15T01:53:55.000000"
    },
    {
      "scrolls": 5,
      "priority": 0,
      "created_at": "2026-03-15T01:53:56.000000"
    }
  ],
  "timestamp": "2026-03-15T01:53:57.000000"
}
```

### 3. 获取已完成的任务结果

**请求:**
```
GET /api/task/{index}
```

**参数:**
- `index` (int): 任务索引（从 0 开始）

**响应:**
```json
{
  "index": 0,
  "status": "completed",
  "scrolls": 10,
  "priority": 1,
  "created_at": "2026-03-15T01:53:50.000000",
  "completed_at": "2026-03-15T01:54:30.000000",
  "result": {
    "total": 120,
    "up_count": 80,
    "down_count": 40,
    "avg_change": 2.45,
    "image_path": "temp_table_1234567890.png"
  },
  "timestamp": "2026-03-15T01:53:57.000000"
}
```

### 4. 获取任务生成的表格图片

**请求:**
```
GET /api/task/{index}/image
```

**响应:** 返回 PNG 图片文件

### 5. 健康检查

**请求:**
```
GET /health
```

**响应:**
```json
{
  "status": "healthy",
  "queue_length": 2,
  "completed_tasks": 5,
  "timestamp": "2026-03-15T01:53:57.000000"
}
```

## 使用示例

### Python 客户端

```python
import requests
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

print("=" * 60)
print("SteamDT 任务队列示例")
print("=" * 60)

# 1. 添加多个任务到队列
print("\n[1] 添加任务到队列...")
tasks = []

# 添加高优先级任务
response = requests.post(f"{BASE_URL}/api/scrape?scrolls=10&priority=2")
result = response.json()
print(f"✓ 高优先级任务已添加 (priority=2)")
tasks.append(result)

# 添加普通优先级任务
response = requests.post(f"{BASE_URL}/api/scrape?scrolls=5&priority=0")
result = response.json()
print(f"✓ 普通优先级任务已添加 (priority=0)")
tasks.append(result)

# 添加低优先级任务
response = requests.post(f"{BASE_URL}/api/scrape?scrolls=5&priority=-1")
result = response.json()
print(f"✓ 低优先级任务已添加 (priority=-1)")
tasks.append(result)

# 2. 监控队列状态
print("\n[2] 监控队列状态...")
while True:
    response = requests.get(f"{BASE_URL}/api/queue")
    status = response.json()
    
    print(f"\n队列长度: {status['queue_length']}")
    print(f"已完成: {status['completed_count']}")
    
    if status['current_task']:
        print(f"当前任务: scrolls={status['current_task']['scrolls']}, priority={status['current_task']['priority']}")
    
    if status['queue_length'] == 0 and not status['current_task']:
        print("✓ 所有任务已完成")
        break
    
    time.sleep(5)

# 3. 获取任务结果
print("\n[3] 获取任务结果...")
for i in range(status['completed_count']):
    response = requests.get(f"{BASE_URL}/api/task/{i}")
    task = response.json()
    
    print(f"\n任务 {i}:")
    print(f"  状态: {task['status']}")
    print(f"  优先级: {task['priority']}")
    print(f"  数据条数: {task['result']['total']}")
    print(f"  平均涨幅: {task['result']['avg_change']}%")
    
    # 下载表格图片
    response = requests.get(f"{BASE_URL}/api/task/{i}/image")
    filename = f'table_{i}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f"  图片已保存: {filename}")

print("\n" + "=" * 60)
print("✓ 所有操作完成！")
print("=" * 60)
```

### cURL 示例

```bash
# 添加高优先级任务
curl -X POST "http://127.0.0.1:5000/api/scrape?scrolls=10&priority=2"

# 添加普通优先级任务
curl -X POST "http://127.0.0.1:5000/api/scrape?scrolls=5&priority=0"

# 获取队列状态
curl "http://127.0.0.1:5000/api/queue" | jq .

# 获取任务结果
curl "http://127.0.0.1:5000/api/task/0" | jq .

# 下载表格图片
curl "http://127.0.0.1:5000/api/task/0/image" -o table.png

# 健康检查
curl "http://127.0.0.1:5000/health" | jq .
```

### JavaScript 客户端

```javascript
const BASE_URL = 'http://127.0.0.1:5000';

// 添加任务
async function addTask(scrolls, priority = 0) {
  const response = await fetch(
    `${BASE_URL}/api/scrape?scrolls=${scrolls}&priority=${priority}`,
    { method: 'POST' }
  );
  return await response.json();
}

// 获取队列状态
async function getQueueStatus() {
  const response = await fetch(`${BASE_URL}/api/queue`);
  return await response.json();
}

// 获取任务结果
async function getTaskResult(index) {
  const response = await fetch(`${BASE_URL}/api/task/${index}`);
  return await response.json();
}

// 监控队列
async function monitorQueue() {
  while (true) {
    const status = await getQueueStatus();
    console.log(`队列长度: ${status.queue_length}, 已完成: ${status.completed_count}`);
    
    if (status.queue_length === 0 && !status.current_task) {
      console.log('所有任务已完成');
      break;
    }
    
    await new Promise(resolve => setTimeout(resolve, 5000));
  }
}

// 使用示例
(async () => {
  // 添加任务
  await addTask(10, 2);  // 高优先级
  await addTask(5, 0);   // 普通优先级
  await addTask(5, -1);  // 低优先级
  
  // 监控队列
  await monitorQueue();
  
  // 获取结果
  const result = await getTaskResult(0);
  console.log(result);
})();
```

## 优先级说明

- **高优先级** (priority > 0): 紧急任务，优先执行
- **普通优先级** (priority = 0): 默认优先级
- **低优先级** (priority < 0): 后台任务，最后执行

### 优先级示例

```bash
# 添加紧急任务（优先级 10）
curl -X POST "http://127.0.0.1:5000/api/scrape?scrolls=10&priority=10"

# 添加普通任务（优先级 0）
curl -X POST "http://127.0.0.1:5000/api/scrape?scrolls=5&priority=0"

# 添加后台任务（优先级 -5）
curl -X POST "http://127.0.0.1:5000/api/scrape?scrolls=5&priority=-5"
```

## 工作流示例

### 完整的任务队列处理流程

```python
import requests
import time

BASE_URL = "http://127.0.0.1:5000"

print("=" * 60)
print("SteamDT 任务队列完整流程")
print("=" * 60)

# 1. 添加任务
print("\n[1] 添加任务...")
tasks = []
for i in range(3):
    priority = 2 - i  # 优先级递减
    response = requests.post(f"{BASE_URL}/api/scrape?scrolls=5&priority={priority}")
    tasks.append(response.json())
    print(f"✓ 任务 {i+1} 已添加 (priority={priority})")

# 2. 等待所有任务完成
print("\n[2] 等待任务完成...")
start_time = time.time()
while True:
    response = requests.get(f"{BASE_URL}/api/queue")
    status = response.json()
    
    elapsed = int(time.time() - start_time)
    print(f"[{elapsed}s] 队列: {status['queue_length']}, 已完成: {status['completed_count']}")
    
    if status['queue_length'] == 0 and not status['current_task']:
        break
    
    time.sleep(2)

# 3. 统计结果
print("\n[3] 统计结果...")
total_data = 0
total_up = 0
total_down = 0

for i in range(status['completed_count']):
    response = requests.get(f"{BASE_URL}/api/task/{i}")
    task = response.json()
    
    if task['status'] == 'completed':
        result = task['result']
        total_data += result['total']
        total_up += result['up_count']
        total_down += result['down_count']

print(f"✓ 总数据条数: {total_data}")
print(f"✓ 总上涨: {total_up}")
print(f"✓ 总下跌: {total_down}")

print("\n" + "=" * 60)
print("✓ 所有操作完成！")
print("=" * 60)
```

## 性能指标

| 操作 | 耗时 | 说明 |
|------|------|------|
| 添加任务 | < 10ms | 立即返回 |
| 获取队列状态 | < 10ms | 立即返回 |
| 爬取（5 次滑动） | 30-40 秒 | 后台处理 |
| 爬取（10 次滑动） | 60-80 秒 | 后台处理 |
| 生成表格图片 | 5-10 秒 | 后台处理 |

## 许可证

MIT License

## 支持

如有问题，请提交 Issue 或联系开发者。
