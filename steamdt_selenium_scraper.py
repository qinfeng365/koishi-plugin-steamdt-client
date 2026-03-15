from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
import time

class SteamDTSeleniumScraper:
    def __init__(self):
        self.url = "https://steamdt.com/changes"
        self.data = []
        self.driver = None
    
    def init_driver(self):
        """初始化 Chrome 驱动"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            print("Chrome 驱动初始化成功")
        except Exception as e:
            print(f"初始化驱动失败: {e}")
            return False
        return True
    
    def fetch_page(self):
        """加载页面并等待数据加载"""
        try:
            print(f"正在加载页面: {self.url}")
            self.driver.get(self.url)
            
            # 等待页面加载完成，最多等待 10 秒
            wait = WebDriverWait(self.driver, 10)
            
            # 尝试等待数据表格或列表加载
            try:
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr, .change-item, [class*='item']")))
                print("页面数据加载完成")
            except:
                print("等待超时，继续处理已加载的内容")
            
            time.sleep(2)  # 额外等待确保 JS 执行完成
            return True
        except Exception as e:
            print(f"加载页面失败: {e}")
            return False
    
    def parse_page(self):
        """解析页面内容"""
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
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
                        print(f"解析行失败: {e}")
                        continue
            
            # 如果没有找到表格，尝试查找其他数据容器
            if not self.data:
                print("未找到表格数据，尝试查找其他容器...")
                divs = soup.find_all('div', class_=True)
                print(f"找到 {len(divs)} 个 div 元素")
                
                # 打印页面结构信息
                print("\n页面主要结构:")
                main_content = soup.find('main') or soup.find('div', class_='main')
                if main_content:
                    print(main_content.prettify()[:1000])
            
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
    
    def close(self):
        """关闭驱动"""
        if self.driver:
            self.driver.quit()
            print("驱动已关闭")
    
    def run(self):
        """执行爬虫"""
        try:
            if not self.init_driver():
                return []
            
            if not self.fetch_page():
                return []
            
            self.parse_page()
            
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
        finally:
            self.close()

if __name__ == "__main__":
    scraper = SteamDTSeleniumScraper()
    scraper.run()
