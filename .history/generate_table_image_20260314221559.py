#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将 SteamDT 异动数据生成为表格图片
"""

import json
import pandas as pd
from datetime import datetime
import sys

def generate_table_image(json_file='steamdt_changes.json', output_file='table.png', rows=30):
    """生成表格图片"""
    
    try:
        # 读取 JSON 数据
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print("错误: 数据为空")
            return False
        
        # 限制行数
        data = data[:rows]
        
        # 创建 DataFrame
        df_data = []
        for i, item in enumerate(data, 1):
            df_data.append({
                '序号': i,
                '时间': item.get('timestamp', '-'),
                '商品': item.get('full_content', '')[:40],
                '旧价格': f"¥{item.get('old_price', '-')}",
                '新价格': f"¥{item.get('new_price', '-')}",
                '价格变化': item.get('price_change', '-'),
                '趋势': item.get('price_trend', '-'),
                '变化%': f"{item.get('price_change_percent', '-')}%"
            })
        
        df = pd.DataFrame(df_data)
        
        # 创建图表
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib import rcParams
        
        # 设置中文字体
        rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        rcParams['axes.unicode_minus'] = False
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(14, max(8, len(df) * 0.3)))
        ax.axis('tight')
        ax.axis('off')
        
        # 创建表格
        table = ax.table(cellText=df.values, colLabels=df.columns, 
                        cellLoc='center', loc='center',
                        colWidths=[0.06, 0.1, 0.25, 0.1, 0.1, 0.12, 0.1, 0.1])
        
        # 设置表格样式
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # 设置表头样式
        for i in range(len(df.columns)):
            cell = table[(0, i)]
            cell.set_facecolor('#667eea')
            cell.set_text_props(weight='bold', color='white')
        
        # 设置行颜色
        for i in range(1, len(df) + 1):
            trend = df.iloc[i-1]['趋势']
            
            for j in range(len(df.columns)):
                cell = table[(i, j)]
                
                if trend == '上涨':
                    cell.set_facecolor('#ffe6e6')
                elif trend == '下跌':
                    cell.set_facecolor('#e6ffe6')
                else:
                    cell.set_facecolor('#f8f9fa' if i % 2 == 0 else 'white')
                
                # 价格变化列加粗
                if j == 5:  # 价格变化列
                    cell.set_text_props(weight='bold')
                    if trend == '上涨':
                        cell.set_text_props(weight='bold', color='#ff4444')
                    elif trend == '下跌':
                        cell.set_text_props(weight='bold', color='#00aa00')
        
        # 添加标题
        fig.suptitle('SteamDT CS2 饰品异动数据表', fontsize=16, fontweight='bold', y=0.98)
        
        # 添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fig.text(0.99, 0.01, f'生成时间: {timestamp}', ha='right', fontsize=8, color='#666')
        
        # 保存图片
        plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"表格图片已生成: {output_file}")
        
        # 显示统计信息
        up_count = sum(1 for item in data if item.get('price_trend') == '上涨')
        down_count = sum(1 for item in data if item.get('price_trend') == '下跌')
        
        print(f"\n数据统计:")
        print(f"  总条数: {len(data)}")
        print(f"  上涨: {up_count}")
        print(f"  下跌: {down_count}")
        
        return True
        
    except ImportError:
        print("错误: 需要安装 pandas 和 matplotlib")
        print("请运行: pip install pandas matplotlib")
        return False
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    json_file = sys.argv[1] if len(sys.argv) > 1 else 'steamdt_changes.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'table.png'
    rows = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    success = generate_table_image(json_file, output_file, rows)
    sys.exit(0 if success else 1)
