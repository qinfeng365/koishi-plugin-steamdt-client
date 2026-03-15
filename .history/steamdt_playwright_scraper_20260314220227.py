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
                await page.wait_for_timeout(5000)  # 等待 5 秒确保 JS 执行
                
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
            
            # 保存 HTML 用于调试
            with open('page_debug.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("页面 HTML 已保存到 page_debug.html")
            
            # 方法 1: 查找所有表格行
            rows = soup.find_all('tr')
            print(f"找到 {len(rows)} 行表格数据")
            
            if rows:
                for row in rows[1:]:  # 跳过表头
                    try:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            item = {
                                'name': cells[0].get_text(strip=True) if len(cells) > 0 else '',
                                'change': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                                'time': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                                'scraped_at': datetime.now().isoformat()
                            }
                            self.data.append(item)
                    except Exception as e:
                        continue
            
            # 方法 2: 查找所有 div 容器中的数据
            if not self.data:
                print("未找到表格，尝试查找 div 容器...")
                
                # 查找所有可能的数据行容器
                containers = soup.find_all('div', class_=re.compile('row|item|change|list', re.I))
                print(f"找到 {len(containers)} 个可能的数据容器")
                
                for container in containers[:50]:  # 限制处理数量
                    try:
                        text = container.get_text(strip=True)
                        if text and len(text) > 10:
                            # 尝试提取数据
                            item = {
                                'content': text[:200],
                                'scraped_at': datetime.now().isoformat()
                            }
                            self.data.append(item)
                    except:
                        continue
            
            # 方法 3: 查找所有文本节点
            if not self.data:
                print("尝试提取所有文本内容...")
                
                # 获取所有 p 标签
                paragraphs = soup.find_all('p')
                print(f"找到 {len(paragraphs)} 个段落")
                
                for p in paragraphs[:30]:
                    text = p.get_text(strip=True)
                    if text and len(text) > 5:
                        item = {
                            'content': text,
                            'scraped_at': datetime.now().isoformat()
                        }
                        self.data.append(item)
            
            # 方法 4: 查找所有 span 标签
            if not self.data:
                print("尝试从 span 标签提取数据...")
                
                spans = soup.find_all('span')
                print(f"找到 {len(spans)} 个 span 标签")
                
                for span in spans[:50]:
                    text = span.get_text(strip=True)
                    if text and len(text) > 3:
                        item = {
                            'content': text,
                            'scraped_at': datetime.now().isoformat()
                        }
                        self.data.append(item)
            
            print(f"\n总共提取 {len(self.data)} 条数据")
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
                print(f"\n成功爬取 {len(self.data)} 条数据")
                self.save_to_json()
                self.save_to_csv()
                
                print("\n前 5 条数据:")
                for i, item in enumerate(self.data[:5], 1):
                    print(f"\n数据 {i}:")
                    print(json.dumps(item, ensure_ascii=False, indent=2))
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
