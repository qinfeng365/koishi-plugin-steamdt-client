import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import csv

class SteamDTScraper:
    def __init__(self):
        self.base_url = "https://steamdt.com/changes"
        self.api_url = "https://steamdt.com/api/changes"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.data = []
    
    def fetch_api_data(self, page=1, limit=100):
        """通过 API 获取异动数据"""
        try:
            params = {
                'page': page,
                'limit': limit
            }
            response = requests.get(self.api_url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API 请求失败: {e}")
            return None
    
    def fetch_page(self):
        """获取页面内容"""
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None
    
    def parse_changes_from_html(self, html):
        """从 HTML 解析异动数据"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找所有可能包含数据的元素
        # 由于是 Vue 应用，数据可能在 script 标签中
        scripts = soup.find_all('script')
        
        for script in scripts:
            if script.string and 'changes' in script.string.lower():
                try:
                    # 尝试提取 JSON 数据
                    content = script.string
                    if '{' in content and '}' in content:
                        # 简单的 JSON 提取
                        start = content.find('{')
                        end = content.rfind('}') + 1
                        if start >= 0 and end > start:
                            json_str = content[start:end]
                            data = json.loads(json_str)
                            if isinstance(data, dict) and 'data' in data:
                                return data['data']
                except:
                    continue
        
        return []
    
    def fetch_all_changes(self, max_pages=10):
        """获取所有异动数据"""
        print("开始爬取数据...")
        
        for page in range(1, max_pages + 1):
            print(f"正在获取第 {page} 页...")
            
            api_data = self.fetch_api_data(page=page)
            
            if api_data:
                if isinstance(api_data, dict) and 'data' in api_data:
                    items = api_data['data']
                elif isinstance(api_data, list):
                    items = api_data
                else:
                    items = []
                
                if not items:
                    print(f"第 {page} 页无数据，停止爬取")
                    break
                
                for item in items:
                    self.data.append({
                        'id': item.get('id', ''),
                        'name': item.get('name', ''),
                        'title': item.get('title', ''),
                        'description': item.get('description', ''),
                        'change_type': item.get('type', ''),
                        'timestamp': item.get('timestamp', ''),
                        'created_at': item.get('created_at', ''),
                        'updated_at': item.get('updated_at', ''),
                        'scraped_at': datetime.now().isoformat()
                    })
                
                print(f"第 {page} 页获取 {len(items)} 条数据")
                time.sleep(1)  # 礼貌延迟
            else:
                print(f"第 {page} 页获取失败")
                break
        
        return self.data
    
    def save_to_json(self, filename='steamdt_changes.json'):
        """保存数据到 JSON 文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到 {filename}")
        except Exception as e:
            print(f"保存失败: {e}")
    
    def save_to_csv(self, filename='steamdt_changes.csv'):
        """保存数据到 CSV 文件"""
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
    
    def run(self, max_pages=10):
        """执行爬虫"""
        self.fetch_all_changes(max_pages=max_pages)
        
        if self.data:
            print(f"\n成功爬取 {len(self.data)} 条数据")
            self.save_to_json()
            self.save_to_csv()
            return self.data
        else:
            print("爬取失败或无数据")
            return []

if __name__ == "__main__":
    scraper = SteamDTScraper()
    data = scraper.run(max_pages=5)
    
    # 打印前几条数据
    if data:
        print("\n前 3 条数据:")
        for item in data[:3]:
            print(json.dumps(item, ensure_ascii=False, indent=2))
