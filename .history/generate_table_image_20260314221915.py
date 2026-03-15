#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将 SteamDT 异动数据生成为高质量表格图片
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
            # 提取商品名称（从 full_content 中）
            content = item.get('full_content', '')
            # 尝试从内容中提取商品名称
            import re
            match = re.search(r'BUFF(.+?)\(', content)
            product_name = match.group(1).strip() if match else content[:30]
            
            df_data.append({
                '序号': i,
                '时间': item.get('timestamp', '-'),
                '商品': product_name,
                '旧价': f"¥{item.get('old_price', '-')}",
                '新价': f"¥{item.get('new_price', '-')}",
                '变化': item.get('price_change', '-'),
                '趋势': item.get('price_trend', '-'),
                '涨幅%': f"{item.get('price_change_percent', '-')}%"
            })
        
        df = pd.DataFrame(df_data)
        
        # 创建图表
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib import rcParams
        
        # 设置中文字体
        rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        rcParams['axes.unicode_minus'] = False
        
        # 计算图表大小
        fig_height = max(10, len(df) * 0.35)
        fig, ax = plt.subplots(figsize=(16, fig_height))
        ax.axis('tight')
        ax.axis('off')
        
        # 创建表格
        table = ax.table(
            cellText=df.values, 
            colLabels=df.columns, 
            cellLoc='center', 
            loc='center',
            colWidths=[0.05, 0.1, 0.25, 0.1, 0.1, 0.12, 0.1, 0.1]
        )
        
        # 设置表格样式
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.2)
        
        # 设置表头样式
        for i in range(len(df.columns)):
            cell = table[(0, i)]
            cell.set_facecolor('#4472C4')
            cell.set_text_props(weight='bold', color='white', fontsize=11)
            cell.set_height(0.08)
        
        # 设置行颜色和样式
        for i in range(1, len(df) + 1):
            trend = df.iloc[i-1]['趋势']
            
            for j in range(len(df.columns)):
                cell = table[(i, j)]
                
                # 根据趋势设置背景色
                if trend == '上涨':
                    cell.set_facecolor('#FFE6E6')
                    cell.set_edgecolor('#FF9999')
                elif trend == '下跌':
                    cell.set_facecolor('#E6F7E6')
                    cell.set_edgecolor('#99CC99')
                else:
                    if i % 2 == 0:
                        cell.set_facecolor('#F5F5F5')
                    else:
                        cell.set_facecolor('white')
                    cell.set_edgecolor('#CCCCCC')
                
                # 设置文字样式
                cell.set_text_props(fontsize=9)
                
                # 价格变化列加粗
                if j == 5:  # 价格变化列
                    cell.set_text_props(weight='bold', fontsize=10)
                    if trend == '上涨':
                        cell.set_text_props(weight='bold', color='#FF4444', fontsize=10)
                    elif trend == '下跌':
                        cell.set_text_props(weight='bold', color='#00AA00', fontsize=10)
                
                # 趋势列加粗
                if j == 6:
                    cell.set_text_props(weight='bold', fontsize=10)
                    if trend == '上涨':
                        cell.set_text_props(weight='bold', color='#FF4444', fontsize=10)
                    elif trend == '下跌':
                        cell.set_text_props(weight='bold', color='#00AA00', fontsize=10)
                
                # 涨幅列加粗
                if j == 7:
                    cell.set_text_props(weight='bold', fontsize=10)
                    if trend == '上涨':
                        cell.set_text_props(weight='bold', color='#FF4444', fontsize=10)
                    elif trend == '下跌':
                        cell.set_text_props(weight='bold', color='#00AA00', fontsize=10)
        
        # 添加标题
        fig.suptitle('SteamDT CS2 饰品异动数据表', fontsize=18, fontweight='bold', y=0.98)
        
        # 添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fig.text(0.99, 0.01, f'生成时间: {timestamp}', ha='right', fontsize=9, color='#666')
        
        # 添加图例
        fig.text(0.01, 0.01, f'总计: {len(data)} 条数据', ha='left', fontsize=9, color='#666')
        
        # 保存图片
        plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
        print(f"表格图片已生成: {output_file}")
        
        # 显示统计信息
        up_count = sum(1 for item in data if item.get('price_trend') == '上涨')
        down_count = sum(1 for item in data if item.get('price_trend') == '下跌')
        
        print(f"\n数据统计:")
        print(f"  总条数: {len(data)}")
        print(f"  上涨: {up_count}")
        print(f"  下跌: {down_count}")
        
        plt.close()
        return True
        
    except ImportError as e:
        print(f"错误: 需要安装依赖库")
        print(f"请运行: pip install pandas matplotlib pillow")
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
