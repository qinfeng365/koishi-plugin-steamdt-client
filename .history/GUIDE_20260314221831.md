# SteamDT 异动数据爬虫 - 完整使用指南

## 📋 项目概述

这是一个完整的 CS2 饰品异动数据爬虫系统，包含：
- **数据爬取** - 从 SteamDT 网站爬取实时异动数据
- **数据格式化** - 支持 JSON、CSV、表格图片等多种格式
- **数据可视化** - 生成美观的表格和报告

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
pip install pandas matplotlib pillow
```

### 2. 爬取数据

```bash
# 基础用法（默认滚动 10 次，获取 200+ 条数据）
python steamdt_scraper_final.py

# 自定义滚动次数
python steamdt_scraper_final.py 5    # 滚动 5 次
python steamdt_scraper_final.py 20   # 滚动 20 次
```

### 3. 生成表格图片

```bash
# 生成前 30 条数据的表格图片
python generate_table_image.py steamdt_changes.json table.png 30

# 生成前 50 条数据的表格图片
python generate_table_image.py steamdt_changes.json table.png 50
```

### 4. 查看数据

- **HTML 查看器** - 打开 `viewer.html` 在浏览器中查看（支持搜索、筛选、分页）
- **表格图片** - 查看 `table.png` 获得美观的表格展示
- **JSON 数据** - 查看 `steamdt_changes.json` 获得原始数据
- **CSV 数据** - 用 Excel 打开 `steamdt_changes.csv`

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `steamdt_scraper_final.py` | 主爬虫脚本（支持滚动加载） |
| `generate_table_image.py` | 表格图片生成脚本 |
| `viewer.html` | 交互式数据查看器 |
| `steamdt_changes.json` | 爬取的原始数据（JSON 格式） |
| `steamdt_changes.csv` | 爬取的原始数据（CSV 格式） |
| `table.png` | 表格图片 |
| `requirements.txt` | Python 依赖列表 |

## 📊 数据格式

### JSON 格式

```json
[
  {
    "timestamp": "今天 22:04",
    "name": "MAC-10 | 绝界之行",
    "old_price": "74.89",
    "new_price": "75",
    "price_change": "74.89 >> 75",
    "price_trend": "上涨",
    "price_change_amount": "3.14",
    "price_change_percent": "4.16",
    "image_url": "https://img.zbt.com/...",
    "full_content": "今天 22:04BUFFMAC-10 | 绝界之行...",
    "scraped_at": "2026-03-14T22:08:15.047942"
  }
]
```

### CSV 格式

| 时间 | 商品 | 旧价格 | 新价格 | 价格变化 | 趋势 | 变化% |
|------|------|--------|--------|----------|------|-------|
| 今天 22:04 | MAC-10 \| 绝界之行 | ¥74.89 | ¥75 | 74.89 >> 75 | 上涨 | 4.16% |

## 🎯 使用场景

### 场景 1: 监测特定商品价格

```python
import asyncio
from steamdt_scraper_final import SteamDTScraper

async def monitor_price():
    scraper = SteamDTScraper(max_scrolls=5)
    data = await scraper.run()
    
    # 筛选特定商品
    ak47_items = [item for item in data if 'AK-47' in item['full_content']]
    print(f"找到 {len(ak47_items)} 条 AK-47 异动数据")
```

### 场景 2: 生成每日报告

```bash
# 创建脚本 daily_report.sh
python steamdt_scraper_final.py 10
python generate_table_image.py steamdt_changes.json report_$(date +%Y%m%d).png 50
```

### 场景 3: 数据分析

```python
import json
import pandas as pd

# 读取数据
with open('steamdt_changes.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 转换为 DataFrame
df = pd.DataFrame(data)

# 统计分析
print(f"上涨商品: {len(df[df['price_trend'] == '上涨'])}")
print(f"下跌商品: {len(df[df['price_trend'] == '下跌'])}")
print(f"平均涨幅: {df['price_change_percent'].astype(float).mean():.2f}%")
```

## ⚙️ 配置选项

### 爬虫配置

```python
from steamdt_scraper_final import SteamDTScraper

scraper = SteamDTScraper(
    output_dir='./data',      # 输出目录
    max_scrolls=10            # 滚动次数
)
```

### 表格图片配置

```bash
# 参数: json_file output_file rows
python generate_table_image.py steamdt_changes.json table.png 50
```

## 🔧 故障排除

### 问题 1: 找不到 Chromium

```bash
playwright install chromium
```

### 问题 2: 页面加载超时

修改 `steamdt_scraper_final.py` 中的超时时间：
```python
await page.goto(self.url, wait_until='networkidle', timeout=60000)  # 60 秒
```

### 问题 3: 中文显示乱码

确保文件编码为 UTF-8，使用以下命令查看：
```bash
file -i steamdt_changes.json
```

### 问题 4: 表格图片生成失败

确保已安装所有依赖：
```bash
pip install pandas matplotlib pillow
```

## 📈 性能指标

| 操作 | 耗时 | 数据量 |
|------|------|--------|
| 爬取（5 次滚动） | 30-40 秒 | 120 条 |
| 爬取（10 次滚动） | 60-80 秒 | 200+ 条 |
| 生成表格图片 | 5-10 秒 | 30-50 行 |
| 生成 HTML 报告 | 2-3 秒 | 全部数据 |

## 💡 最佳实践

1. **定期爬取** - 建议每小时爬取一次，监测价格变化
2. **数据备份** - 定期备份 JSON 文件，便于历史分析
3. **合理延迟** - 避免频繁请求，建议间隔 5-10 分钟
4. **错误处理** - 在生产环境中添加异常处理和日志记录

## 📝 示例工作流

```bash
# 1. 爬取数据
python steamdt_scraper_final.py 10

# 2. 生成表格图片
python generate_table_image.py steamdt_changes.json table_$(date +%Y%m%d_%H%M%S).png 50

# 3. 在浏览器中打开查看器
# 打开 viewer.html

# 4. 导出 CSV 用于 Excel 分析
# 使用 viewer.html 中的导出功能
```

## 📄 许可证

MIT License

## ⚠️ 免责声明

本项目仅供学习和研究使用。使用者需自行承担使用本项目的所有责任。请遵守网站的使用条款和 robots.txt。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题，请提交 Issue 或联系开发者。
