#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SteamDT 异动数据 API 服务 - 异步版本
支持后台任务和 WebSocket 实时推送
"""

from fastapi import FastAPI, HTTPException, WebSocket, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List
import uvicorn
import uuid

# 导入爬虫和生成器
from steamdt_scraper_final import SteamDTScraper
from generate_table_image import generate_table_image

# 创建 FastAPI 应用
app = FastAPI(
    title="SteamDT 异动数据 API",
    description="CS2 饰品异动数据爬虫 API 服务 - 异步版本",
    version="3.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局任务管理
tasks: Dict[str, dict] = {}
websocket_connections: List[WebSocket] = []

class TaskManager:
    """任务管理器"""
    
    @staticmethod
    def create_task(scrolls: int) -> str:
        """创建新任务"""
        task_id = str(uuid.uuid4())
        tasks[task_id] = {
            "id": task_id,
            "status": "pending",
            "scrolls": scrolls,
            "progress": 0,
            "message": "等待中...",
            "data": None,
            "image_path": None,
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        return task_id
    
    @staticmethod
    def update_task(task_id: str, **kwargs):
        """更新任务"""
        if task_id in tasks:
            tasks[task_id].update(kwargs)
    
    @staticmethod
    def get_task(task_id: str) -> dict:
        """获取任务"""
        return tasks.get(task_id)
    
    @staticmethod
    async def broadcast(message: dict):
        """广播消息到所有 WebSocket 连接"""
        for connection in websocket_connections:
            try:
                await connection.send_json(message)
            except:
                pass

@app.get("/")
async def root():
    """根路由"""
    return {
        "name": "SteamDT 异动数据 API - 异步版本",
        "version": "3.0.0",
        "status": "运行中",
        "description": "支持后台任务和 WebSocket 实时推送",
        "endpoints": {
            "POST /api/scrape/async": "异步爬取数据（返回任务 ID）",
            "GET /api/task/{task_id}": "获取任务状态",
            "GET /api/task/{task_id}/result": "获取任务结果",
            "WS /ws": "WebSocket 实时推送",
            "GET /health": "健康检查"
        }
    }

@app.post("/api/scrape/async")
async def scrape_async(scrolls: int = 10, background_tasks: BackgroundTasks = None):
    """
    异步爬取数据
    
    参数:
    - scrolls: 滑动次数（默认 10，范围 1-50）
    
    返回: 任务 ID
    """
    
    if scrolls < 1 or scrolls > 50:
        raise HTTPException(status_code=400, detail="滑动次数必须在 1-50 之间")
    
    # 创建任务
    task_id = TaskManager.create_task(scrolls)
    
    # 在后台运行爬虫
    if background_tasks:
        background_tasks.add_task(run_scraper_async, task_id, scrolls)
    else:
        asyncio.create_task(run_scraper_async(task_id, scrolls))
    
    return {
        "task_id": task_id,
        "status": "已启动",
        "message": "爬虫已启动，请稍候...",
        "timestamp": datetime.now().isoformat()
    }

async def run_scraper_async(task_id: str, scrolls: int):
    """异步运行爬虫"""
    try:
        TaskManager.update_task(task_id, status="running", message="正在爬取数据...")
        await TaskManager.broadcast({
            "type": "task_update",
            "task_id": task_id,
            "status": "running",
            "progress": 10,
            "message": "正在爬取数据..."
        })
        
        # 爬取数据
        scraper = SteamDTScraper(max_scrolls=scrolls)
        data = await scraper.run()
        
        if not data:
            TaskManager.update_task(task_id, status="failed", message="爬取数据失败")
            await TaskManager.broadcast({
                "type": "task_update",
                "task_id": task_id,
                "status": "failed",
                "message": "爬取数据失败"
            })
            return
        
        TaskManager.update_task(task_id, progress=50, message=f"已爬取 {len(data)} 条数据，正在生成表格...")
        await TaskManager.broadcast({
            "type": "task_update",
            "task_id": task_id,
            "progress": 50,
            "message": f"已爬取 {len(data)} 条数据，正在生成表格..."
        })
        
        # 生成表格图片
        image_file = f"temp_table_{task_id}.png"
        success = generate_table_image(
            json_file='steamdt_changes.json',
            output_file=image_file,
            rows=len(data)
        )
        
        if not success:
            TaskManager.update_task(task_id, status="failed", message="生成表格图片失败")
            await TaskManager.broadcast({
                "type": "task_update",
                "task_id": task_id,
                "status": "failed",
                "message": "生成表格图片失败"
            })
            return
        
        # 统计数据
        up_count = sum(1 for item in data if item.get('price_trend') == '上涨')
        down_count = sum(1 for item in data if item.get('price_trend') == '下跌')
        
        valid_percents = []
        for item in data:
            try:
                percent = float(item.get('price_change_percent', 0))
                valid_percents.append(percent)
            except:
                pass
        
        avg_change = sum(valid_percents) / len(valid_percents) if valid_percents else 0
        
        # 更新任务
        TaskManager.update_task(
            task_id,
            status="completed",
            progress=100,
            message=f"完成！共爬取 {len(data)} 条数据",
            data={
                "total": len(data),
                "up_count": up_count,
                "down_count": down_count,
                "avg_change": round(avg_change, 2)
            },
            image_path=image_file,
            completed_at=datetime.now().isoformat()
        )
        
        await TaskManager.broadcast({
            "type": "task_update",
            "task_id": task_id,
            "status": "completed",
            "progress": 100,
            "message": f"完成！共爬取 {len(data)} 条数据",
            "data": {
                "total": len(data),
                "up_count": up_count,
                "down_count": down_count,
                "avg_change": round(avg_change, 2)
            }
        })
    
    except Exception as e:
        TaskManager.update_task(task_id, status="failed", message=f"错误: {str(e)}")
        await TaskManager.broadcast({
            "type": "task_update",
            "task_id": task_id,
            "status": "failed",
            "message": f"错误: {str(e)}"
        })

@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    
    task = TaskManager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return {
        "task_id": task_id,
        "status": task["status"],
        "progress": task["progress"],
        "message": task["message"],
        "created_at": task["created_at"],
        "completed_at": task["completed_at"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/task/{task_id}/result")
async def get_task_result(task_id: str):
    """获取任务结果"""
    
    task = TaskManager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"任务未完成，当前状态: {task['status']}")
    
    return {
        "task_id": task_id,
        "status": task["status"],
        "data": task["data"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/task/{task_id}/image")
async def get_task_image(task_id: str):
    """获取任务生成的表格图片"""
    
    task = TaskManager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"任务未完成，当前状态: {task['status']}")
    
    image_path = task["image_path"]
    if not image_path or not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="图片文件不存在")
    
    return FileResponse(
        path=image_path,
        filename=f'table_{task_id}.png',
        media_type='image/png'
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点 - 实时推送任务进度"""
    
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe":
                task_id = message.get("task_id")
                task = TaskManager.get_task(task_id)
                
                if task:
                    # 发送当前任务状态
                    await websocket.send_json({
                        "type": "task_status",
                        "task_id": task_id,
                        "status": task["status"],
                        "progress": task["progress"],
                        "message": task["message"]
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "任务不存在"
                    })
    
    except Exception as e:
        print(f"WebSocket 错误: {e}")
    
    finally:
        websocket_connections.remove(websocket)

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "active_tasks": len([t for t in tasks.values() if t["status"] == "running"]),
        "total_tasks": len(tasks),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import sys
    
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            port = 5000
    
    print("=" * 60)
    print("SteamDT API Service - Async Version")
    print("=" * 60)
    print(f"\nStarting API service...")
    print(f"Access: http://127.0.0.1:{port}")
    print(f"API Docs: http://127.0.0.1:{port}/docs")
    print("\nMain endpoints:")
    print(f"  - POST /api/scrape/async - Start async scraping")
    print(f"  - GET /api/task/{{task_id}} - Get task status")
    print(f"  - GET /api/task/{{task_id}}/result - Get task result")
    print(f"  - GET /api/task/{{task_id}}/image - Get task image")
    print(f"  - WS /ws - WebSocket real-time updates")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info"
    )
