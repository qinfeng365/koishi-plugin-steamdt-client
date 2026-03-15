#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SteamDT 异动数据 API 服务 - 带任务队列的同步版本
支持任务排队和优先级处理
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os
import time
from datetime import datetime
from typing import Optional
from collections import deque
import uvicorn
import threading
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入爬虫和生成器
from steamdt_scraper_final import SteamDTScraper
from generate_table_image import generate_table_image

# 创建 FastAPI 应用
app = FastAPI(
    title="SteamDT 异动数据 API",
    description="CS2 饰品异动数据爬虫 API 服务 - 带任务队列",
    version="2.1.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1145", "http://127.0.0.1:1145", "http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    max_age=3600,
)

# 任务队列管理
class TaskQueue:
    """任务队列管理器"""
    
    def __init__(self, max_completed_tasks=1000):
        self.queue = deque()
        self.current_task = None
        self.completed_tasks = {}
        self.lock = threading.Lock()
        self.max_completed_tasks = max_completed_tasks
        self.task_counter = 0
    
    def add_task(self, scrolls: int, priority: int = 0) -> dict:
        """添加任务到队列"""
        with self.lock:
            task = {
                "scrolls": scrolls,
                "priority": priority,
                "created_at": datetime.now().isoformat(),
                "status": "queued"
            }
            self.queue.append(task)
            return task
    
    def get_queue_status(self) -> dict:
        """获取队列状态"""
        with self.lock:
            return {
                "queue_length": len(self.queue),
                "current_task": self.current_task,
                "completed_count": len(self.completed_tasks),
                "queue": list(self.queue)
            }
    
    def get_next_task(self) -> Optional[dict]:
        """获取下一个任务"""
        with self.lock:
            if self.queue:
                # 按优先级排序，找到最高优先级任务的索引
                max_idx = 0
                max_priority = self.queue[0]["priority"]
                for idx, task in enumerate(self.queue):
                    if task["priority"] > max_priority:
                        max_priority = task["priority"]
                        max_idx = idx
                
                task = self.queue[max_idx]
                del self.queue[max_idx]  # 按索引删除，避免竞态条件
                self.current_task = task
                return task
            return None
    
    def mark_completed(self, task: dict, result: dict):
        """标记任务完成"""
        with self.lock:
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()
            task["result"] = result
            self.completed_tasks[self.task_counter] = task
            self.task_counter += 1
            self.current_task = None
            self._cleanup_old_tasks()
    
    def mark_failed(self, task: dict, error: str):
        """标记任务失败"""
        with self.lock:
            task["status"] = "failed"
            task["error"] = error
            task["completed_at"] = datetime.now().isoformat()
            self.completed_tasks[self.task_counter] = task
            self.task_counter += 1
            self.current_task = None
            self._cleanup_old_tasks()
    
    def _cleanup_old_tasks(self):
        """清理过期的任务和图片文件（需在锁内调用）"""
        if len(self.completed_tasks) > self.max_completed_tasks:
            # 删除最旧的任务
            oldest_key = min(self.completed_tasks.keys())
            task = self.completed_tasks.pop(oldest_key)
            
            # 清理关联的图片文件
            image_path = task.get("result", {}).get("image_path")
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    logger.debug(f"已删除过期图片: {image_path}")
                except Exception as e:
                    logger.warning(f"删除图片失败 {image_path}: {e}")

# 全局任务队列
task_queue = TaskQueue()

# 后台任务处理线程
def process_queue():
    """处理任务队列的后台线程"""
    while True:
        task = task_queue.get_next_task()
        
        if task:
            try:
                logger.info(f"处理任务: scrolls={task['scrolls']}, priority={task['priority']}")
                
                # 运行爬虫（使用 asyncio.run 确保线程安全）
                scraper = SteamDTScraper(max_scrolls=task['scrolls'])
                try:
                    data = asyncio.run(scraper.run())
                except asyncio.TimeoutError:
                    task_queue.mark_failed(task, "爬虫超时（30秒）")
                    continue
                except Exception as e:
                    logger.error(f"爬虫执行失败: {e}", exc_info=True)
                    task_queue.mark_failed(task, f"爬虫执行失败: {str(e)}")
                    continue
                
                if not data:
                    task_queue.mark_failed(task, "爬取数据失败")
                    continue
                
                # 生成表格图片
                image_file = f"temp_table_{datetime.now().timestamp()}.png"
                image_path = os.path.abspath(image_file)
                try:
                    success = generate_table_image(
                        json_file='steamdt_changes.json',
                        output_file=image_path,
                        rows=len(data)
                    )
                except Exception as e:
                    logger.error(f"生成表格图片失败: {e}", exc_info=True)
                    task_queue.mark_failed(task, f"生成表格图片失败: {str(e)}")
                    continue
                
                if not success:
                    task_queue.mark_failed(task, "生成表格图片失败")
                    continue
                
                # 统计数据
                up_count = sum(1 for item in data if item.get('price_trend') == '上涨')
                down_count = sum(1 for item in data if item.get('price_trend') == '下跌')
                
                valid_percents = []
                for item in data:
                    try:
                        percent = float(item.get('price_change_percent', 0))
                        valid_percents.append(percent)
                    except (ValueError, TypeError) as e:
                        logger.debug(f"数据转换失败: {e}")
                        continue
                
                avg_change = sum(valid_percents) / len(valid_percents) if valid_percents else 0
                
                result = {
                    "total": len(data),
                    "up_count": up_count,
                    "down_count": down_count,
                    "avg_change": round(avg_change, 2),
                    "image_path": image_path
                }
                
                task_queue.mark_completed(task, result)
                logger.info(f"任务完成: {len(data)} 条数据")
            
            except Exception as e:
                logger.error(f"任务处理失败: {str(e)}", exc_info=True)
                task_queue.mark_failed(task, str(e))
        
        else:
            # 队列为空，等待
            time.sleep(1)

# 启动后台处理线程
processor_thread = threading.Thread(target=process_queue, daemon=True)
processor_thread.start()
logger.info("后台任务处理线程已启动")

@app.get("/")
async def root():
    """根路由"""
    return {
        "name": "SteamDT 异动数据 API - 带任务队列",
        "version": "2.1.0",
        "status": "运行中",
        "description": "支持任务队列和优先级处理",
        "endpoints": {
            "POST /api/scrape": "添加爬取任务到队列",
            "GET /api/queue": "获取队列状态",
            "GET /api/task/{index}": "获取已完成的任务结果",
            "GET /api/task/{index}/image": "获取任务生成的表格图片",
            "GET /health": "健康检查"
        }
    }

@app.post("/api/scrape")
async def scrape_with_queue(scrolls: int = 10, priority: int = 0):
    """
    添加爬取任务到队列
    
    参数:
    - scrolls: 滑动次数（默认 10，范围 1-50）
    - priority: 优先级（默认 0，值越大优先级越高）
    """
    
    if scrolls < 1 or scrolls > 50:
        raise HTTPException(status_code=400, detail="滑动次数必须在 1-50 之间")
    
    task = task_queue.add_task(scrolls, priority)
    
    return {
        "status": "已添加到队列",
        "scrolls": scrolls,
        "priority": priority,
        "queue_position": task_queue.get_queue_status()["queue_length"],
        "message": f"任务已添加到队列，当前队列长度: {task_queue.get_queue_status()['queue_length']}",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/queue")
async def get_queue_status():
    """获取队列状态"""
    
    status = task_queue.get_queue_status()
    
    return {
        "queue_length": status["queue_length"],
        "current_task": status["current_task"],
        "completed_count": status["completed_count"],
        "queue": [
            {
                "scrolls": task["scrolls"],
                "priority": task["priority"],
                "created_at": task["created_at"]
            }
            for task in status["queue"]
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/task/{index}")
async def get_task_result(index: int):
    """获取已完成的任务结果"""
    
    if index not in task_queue.completed_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = task_queue.completed_tasks[index]
    
    return {
        "index": index,
        "status": task["status"],
        "scrolls": task["scrolls"],
        "priority": task["priority"],
        "created_at": task["created_at"],
        "completed_at": task["completed_at"],
        "result": task.get("result"),
        "error": task.get("error"),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/task/{index}/image")
async def get_task_image(index: int):
    """获取任务生成的表格图片"""
    
    if index not in task_queue.completed_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = task_queue.completed_tasks[index]
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"任务未完成，状态: {task['status']}")
    
    image_path = task.get("result", {}).get("image_path")
    if not image_path or not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="图片文件不存在")
    
    return FileResponse(
        path=image_path,
        filename=f'table_{index}.png',
        media_type='image/png'
    )

@app.get("/health")
async def health_check():
    """健康检查"""
    status = task_queue.get_queue_status()
    
    return {
        "status": "healthy",
        "queue_length": status["queue_length"],
        "completed_tasks": status["completed_count"],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import sys
    
    port = 1145
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            port = 1145
    
    print("=" * 60)
    print("SteamDT API Service - Queue Version")
    print("=" * 60)
    print(f"\nStarting API service...")
    print(f"Access: http://0.0.0.0:{port} (or use your server IP)")
    print(f"API Docs: http://0.0.0.0:{port}/docs (or use your server IP)")
    print("\nMain endpoints:")
    print(f"  - POST /api/scrape - Add task to queue")
    print(f"  - GET /api/queue - Get queue status")
    print(f"  - GET /api/task/{{index}} - Get task result")
    print(f"  - GET /api/task/{{index}}/image - Get task image")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
