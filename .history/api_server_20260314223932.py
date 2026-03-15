#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SteamDT 异动数据 API 服务 - 实时版本
每次调用时爬取数据并返回表格图片
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os
from datetime import datetime
from io import BytesIO
import uvicorn

# 导入爬虫和生成器
from steamdt_scraper_final import SteamDTScraper
from generate_table_image import generate_table_image

# 创建 FastAPI 应用
app = FastAPI(
    title="SteamDT 异动数据 API",
    description="CS2 饰品异动数据爬虫 API 服务 - 实时版本",
    version="2.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路由"""
    return {
        "name": "SteamDT 异动数据 API - 实时版本",
        "version": "2.0.0",
        "status": "运行中",
        "description": "每次调用时实时爬取数据并返回表格图片",
        "endpoints": {
            "GET /api/scrape/table": "爬取数据并返回表格图片",
            "GET /api/scrape/json": "爬取数据并返回 JSON",
            "GET /api/scrape/csv": "爬取数据并返回 CSV",
            "GET /api/scrape/stats": "爬取数据并返回统计信息",
            "GET /health": "健康检查"
        }
    }

@app.get("/api/scrape/table")
async def scrape_and_get_table(scrolls: int = 10):
    """
    爬取数据并返回表格图片
    
    参数:
    - scrolls: 滑动次数（默认 10，范围 1-50）
    """
    
    if scrolls < 1 or scrolls > 50:
        raise HTTPException(status_code=400, detail="滑动次数必须在 1-50 之间")
    
    try:
        print(f"[{datetime.now()}] 开始爬取数据 (scrolls={scrolls})...")
        
        # 爬取数据
        scraper = SteamDTScraper(max_scrolls=scrolls)
        data = await scraper.run()
        
        if not data:
            raise HTTPException(status_code=500, detail="爬取数据失败")
        
        print(f"[{datetime.now()}] 成功爬取 {len(data)} 条数据，正在生成表格图片...")
        
        # 生成表格图片
        temp_image_file = f"temp_table_{datetime.now().timestamp()}.png"
        success = generate_table_image(
            json_file='steamdt_changes.json',
            output_file=temp_image_file,
            rows=len(data)
        )
        
        if not success or not os.path.exists(temp_image_file):
            raise HTTPException(status_code=500, detail="生成表格图片失败")
        
        print(f"[{datetime.now()}] 表格图片已生成，发送给客户端...")
        
        # 返回图片文件
        return FileResponse(
            path=temp_image_file,
            filename=f'steamdt_table_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png',
            media_type='image/png'
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[{datetime.now()}] 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.get("/api/scrape/json")
async def scrape_and_get_json(scrolls: int = 10, limit: int = None):
    """
    爬取数据并返回 JSON
    
    参数:
    - scrolls: 滑动次数（默认 10，范围 1-50）
    - limit: 限制返回条数（可选）
    """
    
    if scrolls < 1 or scrolls > 50:
        raise HTTPException(status_code=400, detail="滑动次数必须在 1-50 之间")
    
    try:
        print(f"[{datetime.now()}] 开始爬取数据 (scrolls={scrolls})...")
        
        # 爬取数据
        scraper = SteamDTScraper(max_scrolls=scrolls)
        data = await scraper.run()
        
        if not data:
            raise HTTPException(status_code=500, detail="爬取数据失败")
        
        # 限制返回条数
        if limit:
            data = data[:limit]
        
        print(f"[{datetime.now()}] 返回 {len(data)} 条数据")
        
        return {
            "total": len(data),
            "scrolls": scrolls,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[{datetime.now()}] 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.get("/api/scrape/csv")
async def scrape_and_get_csv(scrolls: int = 10):
    """
    爬取数据并返回 CSV
    
    参数:
    - scrolls: 滑动次数（默认 10，范围 1-50）
    """
    
    if scrolls < 1 or scrolls > 50:
        raise HTTPException(status_code=400, detail="滑动次数必须在 1-50 之间")
    
    try:
        print(f"[{datetime.now()}] 开始爬取数据 (scrolls={scrolls})...")
        
        # 爬取数据
        scraper = SteamDTScraper(max_scrolls=scrolls)
        data = await scraper.run()
        
        if not data:
            raise HTTPException(status_code=500, detail="爬取数据失败")
        
        print(f"[{datetime.now()}] 返回 CSV 文件")
        
        # 返回 CSV 文件
        return FileResponse(
            path='steamdt_changes.csv',
            filename=f'steamdt_changes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            media_type='text/csv'
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[{datetime.now()}] 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.get("/api/scrape/stats")
async def scrape_and_get_stats(scrolls: int = 10):
    """
    爬取数据并返回统计信息
    
    参数:
    - scrolls: 滑动次数（默认 10，范围 1-50）
    """
    
    if scrolls < 1 or scrolls > 50:
        raise HTTPException(status_code=400, detail="滑动次数必须在 1-50 之间")
    
    try:
        print(f"[{datetime.now()}] 开始爬取数据 (scrolls={scrolls})...")
        
        # 爬取数据
        scraper = SteamDTScraper(max_scrolls=scrolls)
        data = await scraper.run()
        
        if not data:
            raise HTTPException(status_code=500, detail="爬取数据失败")
        
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
        
        print(f"[{datetime.now()}] 返回统计信息")
        
        return {
            "total": len(data),
            "scrolls": scrolls,
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
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[{datetime.now()}] 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("=" * 60)
    print("SteamDT 异动数据 API 服务 - 实时版本")
    print("=" * 60)
    print("\n启动 API 服务...")
    print("访问地址: http://localhost:8000")
    print("API 文档: http://localhost:8000/docs")
    print("\n主要端点:")
    print("  • GET /api/scrape/table?scrolls=10 - 返回表格图片")
    print("  • GET /api/scrape/json?scrolls=10 - 返回 JSON 数据")
    print("  • GET /api/scrape/csv?scrolls=10 - 返回 CSV 数据")
    print("  • GET /api/scrape/stats?scrolls=10 - 返回统计信息")
    print("\n按 Ctrl+C 停止服务\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
