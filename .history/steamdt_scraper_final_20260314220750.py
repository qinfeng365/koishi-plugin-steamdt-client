#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SteamDT 异动数据爬虫
爬取 https://steamdt.com/changes 的 CS2 饰品异动数据
支持滚动加载更多数据
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
import re
import sys

class SteamDTScraper:
    def __init__(self, output_dir='.', max_scrolls=10):
        self.url = "https://steamdt.com/changes"
        self.data = []
        self.output_dir = output_dir
        self.max_scrolls = max_scrolls
        self.seen_items = set()  # 用于去重
    
    async def fetch_page_with_scroll(self):
        """使用 Playwright 加载页面并滚动加载更多数据"""
        async with async_playwright() as p:
            try:
                print("启动浏览器...")
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                print(f"正在加载页面: {self.url}")
                await page.goto(self.url, wait_until='networkidle', timeout=30000)
                
                print("等待页面加载完成...")
                await page.wait_for_timeout(3000)
                
                # 滚动加载更多数据
                print(f"开始滚动加载数据（最多 {self.max_scrolls} 次）...")
                
                for scroll_count in range(self.max_scrolls):
                    # 获取当前页面高度
                    last_height = await page.evaluate("document.body.scrollHeight")
                    
                    # 滚动到底部
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    
                    # 等待新内容加载
                    await page.wait_for_timeout(2000)
                    
                    # 获取新的页面高度
                    new_height = await page.evaluate("document.body.scrollHeight")
                    
                    print(f"  滚动 {scroll_count + 1}/{self.max_scrolls} - 页面高度: {last_height} -> {new_height}")
                    
                    # 如果高度没有变化，说明已经到底部
                    if new_height == last_height:
                        print("  已到达页面底部")
                        break
                
                # 获取最终页面内容
                content = await page.content()
                await browser.close()
                return content
            except Exception as e:
                print(f"加载页面失败: {e}")
                return None
    
    def parse_page(self, html):
        """解析页面内容，提取异动数据"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找所有异动项目
            change_items = soup.find_all('div', class_=re.compile('item-change-item'))
            print(f"找到 {len(change_items)} 个异动项目")
            
            for item in change_items:
                try:
                    # 提取图片 URL
                    img_elem = item.find('img')
                    img_url = img_elem.get('src', '') if img_elem else ''
                    
                    # 提取所有文本内容
                    all_text = item.get_text(strip=True)
                    
                    # 用于去重
                    item_hash = hash(all_text)
                    if item_hash in self.seen_items:
                        continue
                    self.seen_items.add(item_hash)
                    
                    # 提取价格信息（包含 >> 的部分）
                    price_match = re.search(r'¥\s*([\d.]+)\s*>>\s*([\d.]+)', all_text)
                    old_price = price_match.group(1) if price_match else ''
                    new_price = price_match.group(2) if price_match else ''
                    
                    # 提取时间戳（开头的时间信息）
                    time_match = re.match(r'(今天|昨天|前天)\s+(\d{1,2}):(\d{2})', all_text)
                    timestamp = f"{time_match.group(1)} {time_match.group(2)}:{time_match.group(3)}" if time_match else ''
                    
                    # 提取商品名称（通常在时间后面）
                    name_match = re.search(r'(今天|昨天|前天)\s+\d{1,2}:\d{2}([A-Z0-9\s|]+)\(', all_text)
                    name = name_match.group(2).strip() if name_match else ''
                    
                    # 提取价格变化百分比
                    percent_match = re.search(r'([上下]跌)\s*([\d.]+)\s*\(([\d.]+)%\)', all_text)
                    price_trend = percent_match.group(1) if percent_match else ''
                    price_change_amount = percent_match.group(2) if percent_match else ''
                    price_change_percent = percent_match.group(3) if percent_match else ''
                    
                    if all_text:
                        change_data = {
                            'timestamp': timestamp,
                            'name': name,
                            'old_price': old_price,
                            'new_price': new_price,
                            'price_change': f"{old_price} >> {new_price}",
                            'price_trend': price_trend,
                            'price_change_amount': price_change_amount,
                            'price_change_percent': price_change_percent,
                            'image_url': img_url,
                            'full_content': all_text[:300],
                            'scraped_at': datetime.now().isoformat()
                        }
                        self.data.append(change_data)
                except Exception as e:
                    continue
            
            print(f"成功提取 {len(self.data)} 条异动数据（已去重）")
            return len(self.data) > 0
        except Exception as e:
            print(f"解析页面失败: {e}")
            return False
    
    def save_to_json(self, filename='steamdt_changes.json'):
        """保存数据到 JSON 文件"""
        try:
            filepath = f"{self.output_dir}/{filename}"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到 {filepath}")
            return filepath
        except Exception as e:
            print(f"保存 JSON 失败: {e}")
            return None
    
    def save_to_csv(self, filename='steamdt_changes.csv'):
        """保存数据到 CSV 文件"""
        try:
            if not self.data:
                print("没有数据可保存")
                return None
            
            filepath = f"{self.output_dir}/{filename}"
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
                writer.writeheader()
                writer.writerows(self.data)
            print(f"数据已保存到 {filepath}")
            return filepath
        except Exception as e:
            print(f"保存 CSV 失败: {e}")
            return None
    
    async def run(self):
        """执行爬虫"""
        try:
            html = await self.fetch_page_with_scroll()
            
            if not html:
                print("获取页面失败")
                return []
            
            self.parse_page(html)
            
            if self.data:
                print(f"\n成功爬取 {len(self.data)} 条异动数据")
                json_file = self.save_to_json()
                csv_file = self.save_to_csv()
                
                print(f"\n数据统计:")
                print(f"  总条数: {len(self.data)}")
                print(f"  JSON 文件: {json_file}")
                print(f"  CSV 文件: {csv_file}")
                
                return self.data
            else:
                print("未获取到任何数据")
                return []
        except Exception as e:
            print(f"执行失败: {e}")
            return []

async def main():
    """主函数"""
    # 可以通过参数控制滚动次数
    max_scrolls = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    scraper = SteamDTScraper(max_scrolls=max_scrolls)
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())
