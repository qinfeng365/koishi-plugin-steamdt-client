import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
import re

class SteamDTPlaywrightScraper:
    def __init__(self):
        self.url = "https://steamdt.com/changes"
        self.data = []
    
    async def fetch_page(self):
        """使用 Playwright 加载页面"""
        async with async_playwright() as p:
            try:
                print("启动浏览器...")
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                print(f"正在加载页面: {self.url}")
                await page.goto(self.url, wait_until='networkidle', timeout=30000)
                
                print("等待页面加载完成...")
                await page.wait_for_timeout(5000)
                
                # 获取页面内容
                content = await page.content()
                
                await browser.close()
                return content
            except Exception as e:
                print(f"加载页面失败: {e}")
                return None
    
    def parse_page(self, html):
        """解析页面内容"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找所有异动项目
            change_items = soup.find_all('div', class_=re.compile('item-change-item'))
            print(f"找到 {len(change_items)} 个异动项目")
            
            for item in change_items:
                try:
                    # 提取图片
                    img_elem = item.find('img')
                    img_url = img_elem.get('src', '') if img_elem else ''
                    
                    # 提取商品名称
                    name_elem = item.find('div', class_=re.compile('item-name|name'))
                    name = name_elem.get_text(strip=True) if name_elem else ''
                    
                    # 提取价格信息
                    price_elems = item.find_all('div', class_=re.compile('price|text-.*F87600'))
                    prices = [p.get_text(strip=True) for p in price_elems]
                    
                    # 提取时间
                    time_elem = item.find('div', class_=re.compile('time|date'))
                    timestamp = time_elem.get_text(strip=True) if time_elem else ''
                    
                    # 提取所有文本内容
                    all_text = item.get_text(strip=True)
                    
                    # 如果没有找到结构化数据，尝试从文本中提取
                    if not name:
                        # 尝试从所有文本中提取
                        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                        if lines:
                            name = lines[0] if lines else ''
                    
                    if name or all_text:
                        change_data = {
                            'name': name,
                            'prices': ' | '.join(prices) if prices else '',
                            'timestamp': timestamp,
                            'content': all_text[:500],  # 限制长度
                            'image_url': img_url,
                            'scraped_at': datetime.now().isoformat()
                        }
                        self.data.append(change_data)
                except Exception as e:
                    print(f"解析项目失败: {e}")
                    continue
            
            print(f"成功提取 {len(self.data)} 条异动数据")
            return len(self.data) > 0
        except Exception as e:
            print(f"解析页面失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_to_json(self, filename='steamdt_changes.json'):
        """保存数据到 JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到 {filename}")
        except Exception as e:
            print(f"保存 JSON 失败: {e}")
    
    def save_to_csv(self, filename='steamdt_changes.csv'):
        """保存数据到 CSV"""
        try:
            if not self.data:
                print("没有数据可保存")
                return
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
                writer.writeheader()
                writer.writerows(self.data)
            print(f"数据已保存到 {filename}")
        except Exception as e:
            print(f"保存 CSV 失败: {e}")
    
    async def run(self):
        """执行爬虫"""
        try:
            html = await self.fetch_page()
            
            if not html:
                print("获取页面失败")
                return []
            
            self.parse_page(html)
            
            if self.data:
                print(f"\n成功爬取 {len(self.data)} 条异动数据")
                self.save_to_json()
                self.save_to_csv()
                
                print("\n前 3 条数据:")
                for i, item in enumerate(self.data[:3], 1):
                    print(f"\n数据 {i}:")
                    for key, value in item.items():
                        if key != 'content':
                            print(f"  {key}: {value}")
            else:
                print("未获取到任何数据")
            
            return self.data
        except Exception as e:
            print(f"执行失败: {e}")
            import traceback
            traceback.print_exc()
            return []

async def main():
    scraper = SteamDTPlaywrightScraper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())
