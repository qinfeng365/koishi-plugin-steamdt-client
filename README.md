# SteamDT 异动数据爬虫

这是一个用于爬取 [SteamDT](https://steamdt.com/changes) CS2 饰品异动数据的 Python 爬虫。

## 功能特性

- 爬取 CS2 饰品实时异动数据
- 支持**无限滚动加载**，可获取更多数据
- 提取商品名称、价格变化��时间戳、图片 URL 等信息
- 支持导出为 JSON 和 CSV 格式
- 使用 Playwright 处理动态加载的页面内容
- 自动去重，避免重复数据

## 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

## 使用方法

### 方式 1：运行最终版爬虫（推荐）

**基础用法（默认滚动 10 次）：**
```bash
python steamdt_scraper_final.py
```

**自定义滚动次数：**
```bash
python steamdt_scraper_final.py 5    # 滚动 5 次
python steamdt_scraper_final.py 20   # 滚动 20 次
```

这将爬取数据并保存到：
- `steamdt_changes.json` - JSON 格式
- `steamdt_changes.csv` - CSV 格式

### 方式 2：在 Python 代码中使用

```python
import asyncio
from steamdt_scraper_final import SteamDTScraper

async def main():
    # 创建爬虫实例，max_scrolls 控制滚动次数
    scraper = SteamDTScraper(output_dir='./data', max_scrolls=10)
    data = await scraper.run()
    print(f"爬取了 {len(data)} 条数据")

asyncio.run(main())
```

## 数据格式

### JSON 格式示例

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
    "image_url": "https://img.zbt.com/e/steam/item/730/...",
    "full_content": "今天 22:04BUFFMAC-10 | 绝界之行 (崭新出厂)在售价¥ 74.89 >> 75...",
    "scraped_at": "2026-03-14T22:08:15.047942"
  }
]
```

### CSV 格式

包含以下列：
- `timestamp` - 异动时间
- `name` - 商品名称
- `old_price` - 旧价格
- `new_price` - 新价格
- `price_change` - 价格变化
- `price_trend` - 价格趋势（上涨/下跌）
- `price_change_amount` - 价格变化金额
- `price_change_percent` - 价格变化百分比
- `image_url` - 商品图片 URL
- `full_content` - 完整内容
- `scraped_at` - 爬取时间

## 文件说明

| 文件 | 说明 |
|------|------|
| `steamdt_scraper_final.py` | 最终版爬虫（推荐使用，支持滚动加载） |
| `steamdt_playwright_scraper.py` | Playwright 版爬虫（基础版） |
| `steamdt_scraper.py` | API 版爬虫（已弃用） |
| `steamdt_selenium_scraper.py` | Selenium 版爬虫（已弃用） |
| `requirements.txt` | 依赖列表 |
| `analyze_html.py` | HTML 分析工具 |
| `steamdt_changes.json` | 爬取的数据（JSON 格式） |
| `steamdt_changes.csv` | 爬取的数据（CSV 格式） |

## 爬取的数据示例

```
时间: 今天 22:04
商品: MAC-10 | 绝界之行 (崭新出厂)
价格变化: ¥74.89 >> ¥75
在售数: 92 >> 85
求购价: ¥71 >> ¥65
求购数: 136 >> 133
均价变化: 上涨 3.14 (4.16%)
```

## 性能指标

- **单次爬取**：约 20 条数据
- **5 次滚动**：约 120 条数据
- **10 次滚动**：约 200+ 条数据
- **平均耗时**：5 次滚动约 30-40 秒

## 注意事项

1. 首次运行需要下载 Chromium 浏览器（约 150MB）
2. 爬虫会等待页面完全加载，可能需要 10-15 秒
3. 滚动次数越多，爬取时间越长
4. 请遵守网站的 robots.txt 和使用条款
5. 建议在爬取大量数据时添加延迟以避免对服务器造成压力

## 故障排除

### 问题：找不到 Chromium

**解决方案：**
```bash
playwright install chromium
```

### 问题：页面加载超时

**解决方案：** 检查网络连接，或增加超时时间（修改代码中的 `timeout=30000`）

### 问题：编码错误

**解决方案：** 确保使用 UTF-8 编码打开文件

### 问题：数据为空

**解决方案：** 
1. 检查网络连接
2. 确认网站是否可访问
3. 尝试增加等待时间（修改代码中的 `wait_for_timeout`）

## 许可证

MIT License

## 免责声明

本爬虫仅供学习和研究使用。使用者需自行承担使用本爬虫的所有责任。
