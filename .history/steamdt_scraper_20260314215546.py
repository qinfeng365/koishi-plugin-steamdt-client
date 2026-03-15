import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

class SteamDTScraper:
    def __init__(self):
        self.base_url = "https://steamdt.com/changes"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.data = []
    
    def fetch_page(self):
        """获取页面内容"""
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None
    
    def parse_changes(self, html):
        """解析异动数据"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 根据网站实际结构调整选择器
        # 这里需要根据实际网页结构修改
        changes_container = soup.find('div', class_='changes-container')
        
        if not changes_container:
            print("未找到数据容器，请检查网页结构")
            return []
        
        items = changes_container.find_all('div', class_='change-item')
        
        for item in items:
            try:
                # 根据实际HTML结构提取数据
                title = item.find('h3', class_='title')
                timestamp = item.find('span', class_='time')
                description = item.find('p', class_='description')
                
                if title and timestamp:
                    change_data = {
                        'title': title.get_text(strip=True),
                        'timestamp': timestamp.get_text(strip=True),
                        'description': description.get_text(strip=True) if description else '',
                        'scraped_at': datetime.now().isoformat()
                    }
                    self.data.append(change_data)
            except Exception as e:
                print(f"解析项目失败: {e}")
                continue
        
        return self.data
    
    def save_to_json(self, filename='steamdt_changes.json'):
        """保存数据到JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到 {filename}")
        except Exception as e:
            print(f"保存失败: {e}")
    
    def save_to_csv(self, filename='steamdt_changes.csv'):
        """保存数据到CSV文件"""
        import csv
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
            print(f"保存失败: {e}")
    
    def run(self):
        """执行爬虫"""
        print("开始爬取数据...")
        html = self.fetch_page()
        
        if html:
            self.parse_changes(html)
            print(f"成功爬取 {len(self.data)} 条数据")
            self.save_to_json()
            self.save_to_csv()
            return self.data
        else:
            print("爬取失败")
            return []

if __name__ == "__main__":
    scraper = SteamDTScraper()
    data = scraper.run()
    
    # 打印前几条数据
    if data:
        print("\n前3条数据:")
        for item in data[:3]:
            print(json.dumps(item, ensure_ascii=False, indent=2))
