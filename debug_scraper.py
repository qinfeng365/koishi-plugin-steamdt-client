import requests
from bs4 import BeautifulSoup

# 获取网页内容
url = "https://steamdt.com/changes"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    
    # 保存原始 HTML
    with open('page_source.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 打印页面标题
    print(f"页面标题: {soup.title.string if soup.title else '无标题'}")
    print(f"页面长度: {len(response.text)} 字符")
    
    # 查找所有可能的数据容器
    print("\n=== 查找数据容器 ===")
    
    # 查找所有 table
    tables = soup.find_all('table')
    print(f"找到 {len(tables)} 个表格")
    
    # 查找所有 div
    divs = soup.find_all('div', class_=True)
    print(f"找到 {len(divs)} 个带 class 的 div")
    
    # 打印前几个 div 的 class
    print("\n前 10 个 div 的 class:")
    for i, div in enumerate(divs[:10]):
        print(f"  {i+1}. {div.get('class')}")
    
    # 查找所有 tr (表格行)
    trs = soup.find_all('tr')
    print(f"\n找到 {len(trs)} 个表格行")
    
    if trs:
        print("\n前 3 个表格行的内容:")
        for i, tr in enumerate(trs[:3]):
            print(f"\n行 {i+1}:")
            print(tr.prettify()[:500])
    
    print("\n原始 HTML 已保存到 page_source.html")
    
except Exception as e:
    print(f"错误: {e}")
