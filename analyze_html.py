from bs4 import BeautifulSoup
import json

# 读取 HTML 文件
with open('page_debug.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# 查找所有可能包含异动数据的元素
print("=== 查找数据结构 ===\n")

# 1. 查找所有表格
tables = soup.find_all('table')
print(f"表格数量: {len(tables)}")

# 2. 查找所有 tbody
tbodies = soup.find_all('tbody')
print(f"tbody 数量: {len(tbodies)}")

# 3. 查找所有 tr
trs = soup.find_all('tr')
print(f"tr 数量: {len(trs)}")

if trs:
    print("\n前 5 个 tr 的内容:")
    for i, tr in enumerate(trs[:5]):
        print(f"\ntr {i+1}:")
        print(tr.prettify()[:500])

# 4. 查找所有 class 包含 'change' 的元素
changes = soup.find_all(class_=lambda x: x and 'change' in x.lower())
print(f"\n包含 'change' 的元素: {len(changes)}")

# 5. 查找所有 class 包含 'item' 的元素
items = soup.find_all(class_=lambda x: x and 'item' in x.lower())
print(f"包含 'item' 的元素: {len(items)}")

if items:
    print("\n前 3 个 item 的内容:")
    for i, item in enumerate(items[:3]):
        print(f"\nitem {i+1}:")
        print(item.prettify()[:500])

# 6. 查找所有 script 标签中的 JSON 数据
scripts = soup.find_all('script')
print(f"\nscript 标签数量: {len(scripts)}")

for i, script in enumerate(scripts):
    if script.string:
        content = script.string
        if 'changes' in content.lower() or 'data' in content.lower():
            print(f"\nscript {i+1} 包含数据:")
            print(content[:500])
            
            # 尝试提取 JSON
            if '{' in content:
                try:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start >= 0 and end > start:
                        json_str = content[start:end]
                        data = json.loads(json_str)
                        print(f"成功解析 JSON，键: {list(data.keys())[:5]}")
                except:
                    pass

# 7. 查找所有 data 属性
print("\n=== 查找 data 属性 ===")
elements_with_data = soup.find_all(attrs={'data-*': True})
print(f"包含 data 属性的元素: {len(elements_with_data)}")

# 8. 查找所有 div 并按 class 分类
divs = soup.find_all('div', class_=True)
classes = {}
for div in divs:
    class_str = ' '.join(div.get('class', []))
    if class_str not in classes:
        classes[class_str] = 0
    classes[class_str] += 1

print("\n=== div class 统计 ===")
for cls, count in sorted(classes.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"{cls}: {count}")
