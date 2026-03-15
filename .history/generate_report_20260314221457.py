#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成 SteamDT 异动数据的 HTML 报告
"""

import json
import csv
from datetime import datetime
from pathlib import Path

def generate_html_report(json_file='steamdt_changes.json', output_file='report.html'):
    """生成 HTML 报告"""
    
    # 读取 JSON 数据
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {json_file}")
        return False
    
    if not data:
        print("错误: 数据为空")
        return False
    
    # 统计数据
    total_count = len(data)
    up_count = sum(1 for item in data if item.get('price_trend') == '上涨')
    down_count = sum(1 for item in data if item.get('price_trend') == '下跌')
    
    # 计算平均涨幅
    valid_percents = [float(item['price_change_percent']) for item in data 
                      if item.get('price_change_percent')]
    avg_change = sum(valid_percents) / len(valid_percents) if valid_percents else 0
    
    # 找出最大涨幅和最大跌幅
    max_up = max((item for item in data if item.get('price_trend') == '上涨'), 
                 key=lambda x: float(x.get('price_change_percent', 0)), default=None)
    max_down = max((item for item in data if item.get('price_trend') == '下跌'), 
                   key=lambda x: float(x.get('price_change_percent', 0)), default=None)
    
    # 生成表格行
    table_rows = ''
    for i, item in enumerate(data[:100], 1):  # 显示前 100 条
        trend_class = 'up' if item.get('price_trend') == '上涨' else 'down' if item.get('price_trend') == '下跌' else 'neutral'
        
        table_rows += f'''
        <tr class="trend-{trend_class}">
            <td>{i}</td>
            <td><img src="{item.get('image_url', '')}" alt="商品" class="item-img"></td>
            <td>{item.get('timestamp', '-')}</td>
            <td class="item-name">{item.get('full_content', '')[:60]}</td>
            <td class="price">¥{item.get('old_price', '-')}</td>
            <td class="price">¥{item.get('new_price', '-')}</td>
            <td class="price-change">{item.get('price_change', '-')}</td>
            <td class="trend-badge {trend_class}">{item.get('price_trend', '-')}</td>
            <td class="percent">{item.get('price_change_percent', '-')}%</td>
        </tr>
        '''
    
    # 生成 HTML
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SteamDT 异动数据报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        
        .stat-card h3 {{
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .stat-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-card.up .value {{
            color: #ff4444;
        }}
        
        .stat-card.down .value {{
            color: #00aa00;
        }}
        
        .highlights {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .highlight-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #667eea;
        }}
        
        .highlight-card.up {{
            border-left-color: #ff4444;
        }}
        
        .highlight-card.down {{
            border-left-color: #00aa00;
        }}
        
        .highlight-card h4 {{
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        
        .highlight-card .content {{
            font-size: 14px;
            color: #333;
        }}
        
        .table-section {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .table-header {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .table-header h2 {{
            font-size: 18px;
            color: #333;
        }}
        
        .table-wrapper {{
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        thead {{
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}
        
        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
            font-size: 13px;
            text-transform: uppercase;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
            font-size: 13px;
        }}
        
        tbody tr:hover {{
            background: #f8f9fa;
        }}
        
        .item-img {{
            width: 40px;
            height: 40px;
            border-radius: 4px;
            object-fit: cover;
            background: #f0f0f0;
        }}
        
        .item-name {{
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        .price {{
            text-align: right;
            font-family: 'Monaco', monospace;
            font-weight: 500;
        }}
        
        .price-change {{
            text-align: right;
            font-weight: 600;
        }}
        
        .trend-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            text-align: center;
        }}
        
        .trend-badge.up {{
            background: #ffe6e6;
            color: #ff4444;
        }}
        
        .trend-badge.down {{
            background: #e6ffe6;
            color: #00aa00;
        }}
        
        .trend-badge.neutral {{
            background: #f0f0f0;
            color: #666;
        }}
        
        .percent {{
            text-align: right;
            font-weight: 600;
        }}
        
        tbody tr.trend-up {{
            background: rgba(255, 68, 68, 0.02);
        }}
        
        tbody tr.trend-down {{
            background: rgba(0, 170, 0, 0.02);
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            margin-top: 30px;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            
            .container {{
                max-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 SteamDT CS2 饰品异动数据报告</h1>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>总数据条数</h3>
                <div class="value">{total_count}</div>
            </div>
            <div class="stat-card up">
                <h3>上涨商品</h3>
                <div class="value">{up_count}</div>
            </div>
            <div class="stat-card down">
                <h3>下跌商品</h3>
                <div class="value">{down_count}</div>
            </div>
            <div class="stat-card">
                <h3>平均涨幅</h3>
                <div class="value">{avg_change:.2f}%</div>
            </div>
        </div>
        
        <div class="highlights">
            {f'''<div class="highlight-card up">
                <h4>📈 最大涨幅</h4>
                <div class="content">
                    <p><strong>{max_up.get("full_content", "")[:50]}</strong></p>
                    <p>涨幅: <strong>{max_up.get("price_change_percent", "-")}%</strong></p>
                    <p>价格: ¥{max_up.get("old_price", "-")} → ¥{max_up.get("new_price", "-")}</p>
                </div>
            </div>''' if max_up else ''}
            
            {f'''<div class="highlight-card down">
                <h4>📉 最大跌幅</h4>
                <div class="content">
                    <p><strong>{max_down.get("full_content", "")[:50]}</strong></p>
                    <p>跌幅: <strong>{max_down.get("price_change_percent", "-")}%</strong></p>
                    <p>价格: ¥{max_down.get("old_price", "-")} → ¥{max_down.get("new_price", "-")}</p>
                </div>
            </div>''' if max_down else ''}
        </div>
        
        <div class="table-section">
            <div class="table-header">
                <h2>异动数据表 (前 100 条)</h2>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>图片</th>
                            <th>时间</th>
                            <th>商品</th>
                            <th>旧价格</th>
                            <th>新价格</th>
                            <th>价格变化</th>
                            <th>趋势</th>
                            <th>变化百分比</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p>数据来源: SteamDT | 总共 {total_count} 条数据 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
'''
    
    # 写入文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ HTML 报告已生成: {output_file}")
        return True
    except Exception as e:
        print(f"✗ 生成报告失败: {e}")
        return False

if __name__ == '__main__':
    import sys
    
    json_file = sys.argv[1] if len(sys.argv) > 1 else 'steamdt_changes.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'report.html'
    
    success = generate_html_report(json_file, output_file)
    sys.exit(0 if success else 1)
