# SteamDT 异动数据 API 文档 - 异步版本

## 概述

这是一个支持**异步处理**和 **WebSocket 实时推送**的 RESTful API 服务。每次调用时实时爬取数据，支持后台任务和实时进度推送。

## 快速开始

### 启动服务

```bash
python api_server_async.py 5000
```

服务将在 `http://127.0.0.1:5000` 启动

### 访问 API 文档

- **Swagger UI**: http://127.0.0.1:5000/docs
- **ReDoc**: http://127.0.0.1:5000/redoc

## API 端点

### 1. 异步启动爬虫 ⭐

**请求:**
```
POST /api/scrape/async?scrolls=10
```

**参数:**
- `scrolls` (int): 滑动次数，范围 1-50（默认 10）

**响应:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "已启动",
  "message": "爬虫已启动，请稍候...",
  "timestamp": "2026-03-14T22:36:00.000000"
}
```

### 2. 获取任务状态

**请求:**
```
GET /api/task/{task_id}
```

**响应:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": 50,
  "message": "已爬取 120 条数据，正在生成表格...",
  "created_at": "2026-03-14T22:36:00.000000",
  "completed_at": null,
  "timestamp": "2026-03-14T22:36:10.000000"
}
```

**状态值:**
- `pending` - 等待中
- `running` - 运行中
- `completed` - 已完成
- `failed` - 失败

### 3. 获取任务结果

**请求:**
```
GET /api/task/{task_id}/result
```

**响应:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "data": {
    "total": 120,
    "up_count": 80,
    "down_count": 40,
    "avg_change": 2.45
  },
  "timestamp": "2026-03-14T22:36:30.000000"
}
```

### 4. 获取任务生成的表格图片

**请求:**
```
GET /api/task/{task_id}/image
```

**响应:** 返回 PNG 图片文件

### 5. WebSocket 实时推送 ⭐

**连接:**
```
WS ws://127.0.0.1:5000/ws
```

**订阅任务:**
```json
{
  "type": "subscribe",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**接收更新:**
```json
{
  "type": "task_update",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": 50,
  "message": "已爬取 120 条数据，正在生成表格..."
}
```

### 6. 健康检查

**请求:**
```
GET /health
```

**响应:**
```json
{
  "status": "healthy",
  "active_tasks": 2,
  "total_tasks": 10,
  "timestamp": "2026-03-14T22:36:00.000000"
}
```

## 使用示例

### Python 客户端 - 异步方式

```python
import requests
import time
import json

BASE_URL = "http://127.0.0.1:5000"

# 1. 启动异步爬虫
print("启动异步爬虫...")
response = requests.post(f"{BASE_URL}/api/scrape/async?scrolls=10")
result = response.json()
task_id = result["task_id"]
print(f"任务 ID: {task_id}")

# 2. 轮询获取任务状态
print("\n等待任务完成...")
while True:
    response = requests.get(f"{BASE_URL}/api/task/{task_id}")
    task = response.json()
    
    print(f"进度: {task['progress']}% - {task['message']}")
    
    if task["status"] in ["completed", "failed"]:
        break
    
    time.sleep(2)

# 3. 获取任务结果
if task["status"] == "completed":
    response = requests.get(f"{BASE_URL}/api/task/{task_id}/result")
    result = response.json()
    print(f"\n数据统计:")
    print(f"  总条数: {result['data']['total']}")
    print(f"  上涨: {result['data']['up_count']}")
    print(f"  下跌: {result['data']['down_count']}")
    print(f"  平均涨幅: {result['data']['avg_change']}%")
    
    # 4. 下载表格图片
    response = requests.get(f"{BASE_URL}/api/task/{task_id}/image")
    with open(f'table_{task_id}.png', 'wb') as f:
        f.write(response.content)
    print(f"\n表格图片已保存: table_{task_id}.png")
```

### Python 客户端 - WebSocket 实时推送

```python
import asyncio
import websockets
import json

async def monitor_task(task_id):
    """使用 WebSocket 监听任务进度"""
    
    uri = "ws://127.0.0.1:5000/ws"
    
    async with websockets.connect(uri) as websocket:
        # 订阅任务
        await websocket.send(json.dumps({
            "type": "subscribe",
            "task_id": task_id
        }))
        
        # 接收更新
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data["type"] == "task_update":
                print(f"进度: {data['progress']}% - {data['message']}")
                
                if data["status"] in ["completed", "failed"]:
                    break

# 使用
import requests

# 启动爬虫
response = requests.post("http://127.0.0.1:5000/api/scrape/async?scrolls=10")
task_id = response.json()["task_id"]

# 监听进度
asyncio.run(monitor_task(task_id))
```

### JavaScript 客户端 - WebSocket

```javascript
const BASE_URL = 'http://127.0.0.1:5000';
const WS_URL = 'ws://127.0.0.1:5000/ws';

// 启动异步爬虫
async function startScraping() {
  const response = await fetch(`${BASE_URL}/api/scrape/async?scrolls=10`, {
    method: 'POST'
  });
  const result = await response.json();
  return result.task_id;
}

// 使用 WebSocket 监听进度
function monitorTask(taskId) {
  const ws = new WebSocket(WS_URL);
  
  ws.onopen = () => {
    // 订阅任务
    ws.send(JSON.stringify({
      type: 'subscribe',
      task_id: taskId
    }));
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'task_update') {
      console.log(`进度: ${data.progress}% - ${data.message}`);
      
      if (data.status === 'completed') {
        console.log('任务完成！');
        console.log(data.data);
        ws.close();
      }
    }
  };
}

// 使用
(async () => {
  const taskId = await startScraping();
  console.log(`任务 ID: ${taskId}`);
  monitorTask(taskId);
})();
```

### cURL 示例

```bash
# 启动异步爬虫
TASK_ID=$(curl -X POST "http://127.0.0.1:5000/api/scrape/async?scrolls=10" | jq -r '.task_id')
echo "Task ID: $TASK_ID"

# 获取任务状态
curl "http://127.0.0.1:5000/api/task/$TASK_ID"

# 获取任务结果
curl "http://127.0.0.1:5000/api/task/$TASK_ID/result"

# 下载表格图片
curl "http://127.0.0.1:5000/api/task/$TASK_ID/image" -o table.png
```

## 工作流示例

### 完整的异步数据获取流程

```python
import requests
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

print("=" * 60)
print("SteamDT 异步数据获取流程")
print("=" * 60)

# 1. 启动异步爬虫
print("\n[1/4] 启动异步爬虫...")
response = requests.post(f"{BASE_URL}/api/scrape/async?scrolls=10")
task_id = response.json()["task_id"]
print(f"✓ 任务已启动，ID: {task_id}")

# 2. 轮询获取任务状态
print("\n[2/4] 等待任务完成...")
start_time = time.time()
while True:
    response = requests.get(f"{BASE_URL}/api/task/{task_id}")
    task = response.json()
    
    elapsed = int(time.time() - start_time)
    print(f"  [{elapsed}s] 进度: {task['progress']}% - {task['message']}")
    
    if task["status"] in ["completed", "failed"]:
        break
    
    time.sleep(2)

# 3. 获取任务结果
if task["status"] == "completed":
    print("\n[3/4] 获取任务结果...")
    response = requests.get(f"{BASE_URL}/api/task/{task_id}/result")
    result = response.json()
    
    print(f"✓ 数据统计:")
    print(f"  总条数: {result['data']['total']}")
    print(f"  上涨: {result['data']['up_count']}")
    print(f"  下跌: {result['data']['down_count']}")
    print(f"  平均涨幅: {result['data']['avg_change']}%")
    
    # 4. 下载表格图片
    print("\n[4/4] 下载表格图片...")
    response = requests.get(f"{BASE_URL}/api/task/{task_id}/image")
    filename = f'table_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f"✓ 表格图片已保存: {filename}")
else:
    print(f"\n✗ 任务失败: {task['message']}")

print("\n" + "=" * 60)
print("✓ 所有操作完成！")
print("=" * 60)
```

## 异步处理的优势

1. **非阻塞** - 不需要等待爬虫完成，立即返回任务 ID
2. **实时推送** - 通过 WebSocket 实时推送进度
3. **并发处理** - 支持多个任务同时运行
4. **资源高效** - 充分利用系统资源
5. **用户体验** - 可以显示进度条和实时更新

## 性能指标

| 操作 | 耗时 | 数据量 |
|------|------|--------|
| 爬取（5 次滑动） | 30-40 秒 | 120 条 |
| 爬取（10 次滑动） | 60-80 秒 | 200+ 条 |
| 生成表格图片 | 5-10 秒 | 全部数据 |
| API 响应 | < 100ms | - |

## 许可证

MIT License

## 支持

如有问题，请提交 Issue 或联系开发者。
