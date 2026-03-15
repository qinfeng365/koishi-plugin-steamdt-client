#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SteamDT 异动数据 API 服务
提供 RESTful API 接口获取和处理数据
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os
from datetime import datetime
from typing import Optional
import uvicorn

# 导入爬虫和生成器
from steamdt_scraper_final import SteamDTScraper
from generate_table_image import generate_table_image

# 创建 FastAPI 应用
app = FastAPI(
    title="SteamDT 异动数据 API",
    description="CS2 饰品异动数据爬虫 API 服务",
    version="1.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局状态
scraping_status = {
    "is_running": False,
    "progress": 0,
    "total": 0,
    "message": "就绪"
}

# 挂载静态文件
if os.path.exists('viewer.html'):
    app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def root():
    """根路由"""
    return {
        "name": "SteamDT 异动数据 API",
        "version": "1.0.0",
        "status": "运行中",
        "endpoints": {
            "GET /api/status": "获取爬虫状态",
            "POST /api/scrape": "开始爬取数据",
            "GET /api/data": "获取爬取的数据",
            "GET /api/data/json": "下载 JSON 数据",
            "GET /api/data/csv": "下载 CSV 数据",
            "GET /api/table": "下载表格图片",
            "GET /api/stats": "获取数据统计",
            "GET /viewer": "打开数据查看器"
        }
    }

@app.get("/api/status")
async def get_status():
    """获取爬虫状态"""
    return {
        "is_running": scraping_status["is_running"],
        "progress": scraping_status["progress"],
        "total": scraping_status["total"],
        "message": scraping_status["message"],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/scrape")
async def scrape_data(scrolls: int = 10, background_tasks: BackgroundTasks = None):
    """
    开始爬取数据
    
    参数:
    - scrolls: 滑动次数（默认 10）
    """
    
    if scraping_status["is_running"]:
        raise HTTPException(status_code=400, detail="爬虫已在运行中")
    
    if scrolls < 1 or scrolls > 50:
        raise HTTPException(status_code=400, detail="滑动次数必须在 1-50 之间")
    
    # 在后台运行爬虫
    if background_tasks:
        background_tasks.add_task(run_scraper, scrolls)
    else:
        await run_scraper(scrolls)
    
    return {
        "status": "已启动",
        "scrolls": scrolls,
        "message": "爬虫已启动，请稍候...",
        "timestamp": datetime.now().isoformat()
    }

async def run_scraper(scrolls: int):
    """运行爬虫"""
    try:
        scraping_status["is_running"] = True
        scraping_status["message"] = "正在爬取数据..."
        scraping_status["progress"] = 0
        
        scraper = SteamDTScraper(max_scrolls=scrolls)
        data = await scraper.run()
        
        if data:
            scraping_status["total"] = len(data)
            scraping_status["progress"] = 50
            scraping_status["message"] = "正在生成表格图片..."
            
            # 生成表格图片
            generate_table_image(
                json_file='steamdt_changes.json',
                output_file='table.png',
                rows=len(data)
            )
            
            scraping_status["progress"] = 100
            scraping_status["message"] = f"完成！共爬取 {len(data)} 条数据"
        else:
            scraping_status["message"] = "爬取失败"
    
    except Exception as e:
        scraping_status["message"] = f"错误: {str(e)}"
    
    finally:
        scraping_status["is_running"] = False

@app.get("/api/data")
async def get_data(limit: Optional[int] = None):
    """
    获取爬取的数据
    
    参数:
    - limit: 限制返回条数（可选）
    """
    
    if not os.path.exists('steamdt_changes.json'):
        raise HTTPException(status_code=404, detail="数据文件不存在，请先爬取数据")
    
    try:
        with open('steamdt_changes.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if limit:
            data = data[:limit]
        
        return {
            "total": len(data),
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取数据失败: {str(e)}")

@app.get("/api/data/json")
async def download_json():
    """下载 JSON 数据"""
    
    if not os.path.exists('steamdt_changes.json'):
        raise HTTPException(status_code=404, detail="数据文件不存在")
    
    return FileResponse(
        path='steamdt_changes.json',
        filename=f'steamdt_changes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
        media_type='application/json'
    )

@app.get("/api/data/csv")
async def download_csv():
    """下载 CSV 数据"""
    
    if not os.path.exists('steamdt_changes.csv'):
        raise HTTPException(status_code=404, detail="CSV 文件不存在")
    
    return FileResponse(
        path='steamdt_changes.csv',
        filename=f'steamdt_changes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        media_type='text/csv'
    )

@app.get("/api/table")
async def download_table():
    """下载表格图片"""
    
    if not os.path.exists('table.png'):
        raise HTTPException(status_code=404, detail="表格图片不存在，请先爬取数据")
    
    return FileResponse(
        path='table.png',
        filename=f'table_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png',
        media_type='image/png'
    )

@app.get("/api/stats")
async def get_stats():
    """获取数据统计"""
    
    if not os.path.exists('steamdt_changes.json'):
        raise HTTPException(status_code=404, detail="数据文件不存在")
    
    try:
        with open('steamdt_changes.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 统计数据
        up_count = sum(1 for item in data if item.get('price_trend') == '上涨')
        down_count = sum(1 for item in data if item.get('price_trend') == '下跌')
        
        # 计算平均涨幅
        valid_percents = []
        for item in data:
            try:
                percent = float(item.get('price_change_percent', 0))
                valid_percents.append(percent)
            except:
                pass
        
        avg_change = sum(valid_percents) / len(valid_percents) if valid_percents else 0
        
        # 找出最大涨幅和最大跌幅
        max_up = None
        max_up_percent = -999
        max_down = None
        max_down_percent = 999
        
        for item in data:
            try:
                percent = float(item.get('price_change_percent', 0))
                if item.get('price_trend') == '上涨' and percent > max_up_percent:
                    max_up = item
                    max_up_percent = percent
                elif item.get('price_trend') == '下跌' and percent < max_down_percent:
                    max_down = item
                    max_down_percent = percent
            except:
                pass
        
        return {
            "total": len(data),
            "up_count": up_count,
            "down_count": down_count,
            "avg_change": round(avg_change, 2),
            "max_up": {
                "percent": round(max_up_percent, 2),
                "content": max_up.get('full_content', '')[:100] if max_up else None
            } if max_up else None,
            "max_down": {
                "percent": round(max_down_percent, 2),
                "content": max_down.get('full_content', '')[:100] if max_down else None
            } if max_down else None,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"统计失败: {str(e)}")

@app.get("/viewer")
async def viewer():
    """打开数据查看器"""
    
    if not os.path.exists('viewer.html'):
        raise HTTPException(status_code=404, detail="查看器文件不存在")
    
    return FileResponse(path='viewer.html', media_type='text/html')

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("=" * 60)
    print("SteamDT 异动数据 API 服务")
    print("=" * 60)
    print("\n启动 API 服务...")
    print("访问地址: http://localhost:8000")
    print("API 文档: http://localhost:8000/docs")
    print("数据查看器: http://localhost:8000/viewer")
    print("\n按 Ctrl+C 停止服务\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
