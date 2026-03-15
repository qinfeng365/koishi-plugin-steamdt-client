import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime

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
                await page.wait_for_timeout(3000)  # 等待 3 秒确保 JS 执行
                
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
            
            # 查找所有表格行
            rows = soup.find_all('tr')
            print(f"找到 {len(rows)} 行数据")
            
            if rows:
                for row in rows[1:]:  # 跳过表头
                    try:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            item = {
                                'name': cells[0].get_text(strip=True),
                                'change': cells[1].get_text(strip=True),
                                'time': cells[2].get_text(strip=True),
                                'scraped_at': datetime.now().isoformat()
                            }
                            self.data.append(item)
                    except Exception as e:
                        continue
            
            # 如果没有找到表格，尝试查找其他数据容器
            if not self.data:
                print("未找到表格数据，尝试查找其他容器...")
                
                # 查找所有可能的数据行
                items = soup.find_all(['div', 'li'], class_=True)
                print(f"找到 {len(items)} 个可能的数据元素")
                
                # 打印页面结构
                print("\n页面主要内容:")
                main = soup.find('main') or soup.find('div', class_='main-content')
                if main:
                    text = main.get_text(strip=True)[:500]
                    print(text)
            
            return len(self.data) > 0
        except Exception as e:
            print(f"解析页面失败: {e}")
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
                print(f"\n成功爬取 {len(self.data)} 条数据")
                self.save_to_json()
                self.save_to_csv()
                
                print("\n前 3 条数据:")
                for item in self.data[:3]:
                    print(json.dumps(item, ensure_ascii=False, indent=2))
            else:
                print("未获取到任何数据")
            
            return self.data
        except Exception as e:
            print(f"执行失败: {e}")
            return []

async def main():
    scraper = SteamDTPlaywrightScraper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())
