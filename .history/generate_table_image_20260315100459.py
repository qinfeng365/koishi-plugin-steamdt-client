#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将 SteamDT 异动数据生成为高质量表格图片
从 full_content 中解析所有数据
"""

import json
import pandas as pd
from datetime import datetime
import sys
import re
import logging

logger = logging.getLogger(__name__)

def parse_full_content(content):
    """从 full_content 中解析所有数据"""
    
    result = {
        'timestamp': '',
        'platform': '',
        'product': '',
        'wear': '',
        'old_price': '',
        'new_price': '',
        'old_count': '',
        'new_count': '',
        'buy_price': '',
        'buy_count': '',
        'change_amount': '',
        'change_percent': ''
    }
    
    try:
        # 提取时间 (今天/昨天/前天 HH:MM)
        time_match = re.match(r'(今天|昨天|前天)\s+(\d{1,2}):(\d{2})', content)
        if time_match:
            result['timestamp'] = f"{time_match.group(1)} {time_match.group(2)}:{time_match.group(3)}"
        
        # 提取平台 (BUFF/YOUPIN等)
        platform_match = re.search(r'(BUFF|YOUPIN|C5GAME|Steam)', content)
        if platform_match:
            result['platform'] = platform_match.group(1)
        
        # 提取商品名称和磨损度
        # 格式: 平台商品名 | 皮肤名 (磨损度)
        product_match = re.search(r'(?:BUFF|YOUPIN|C5GAME|Steam)(.+?)\(([^)]+)\)', content)
        if product_match:
            full_name = product_match.group(1).strip()
            result['wear'] = product_match.group(2).strip()
            
            # 分离商品和皮肤名
            if '|' in full_name:
                parts = full_name.split('|')
                result['product'] = parts[0].strip()
                result['skin'] = parts[1].strip() if len(parts) > 1 else ''
            else:
                result['product'] = full_name
        
        # 提取在售价格变化 (在售价¥ XXX >> YYY)
        price_match = re.search(r'在售价¥\s*([\d.]+)\s*>>\s*([\d.]+)', content)
        if price_match:
            result['old_price'] = price_match.group(1)
            result['new_price'] = price_match.group(2)
        
        # 提取在售数量变化 (在售数XXX >> YYY)
        count_match = re.search(r'在售数(\d+)\s*>>\s*(\d+)', content)
        if count_match:
            result['old_count'] = count_match.group(1)
            result['new_count'] = count_match.group(2)
        
        # 提取求购价格 (求购价¥ XXX >> YYY)
        buy_price_match = re.search(r'求购价¥\s*([\d.]+)\s*>>\s*([\d.]+)', content)
        if buy_price_match:
            result['buy_price'] = buy_price_match.group(1)
        
        # 提取求购数量 (求购数¥ XXX >> YYY)
        buy_count_match = re.search(r'求购数¥\s*([\d.]+)\s*>>\s*([\d.]+)', content)
        if buy_count_match:
            result['buy_count'] = buy_count_match.group(1)
        
        # 提取均价变化 (上涨/下跌 XXX (YYY%))
        change_match = re.search(r'(上涨|下跌)\s*([-\d.]+)\s*\(([-\d.]+)%\)', content)
        if change_match:
            trend = change_match.group(1)
            amount = change_match.group(2)
            percent = change_match.group(3)
            
            result['change_amount'] = amount
            result['change_percent'] = percent
            
            # 如果是下跌，百分比前加负号
            if trend == '下跌' and not percent.startswith('-'):
                result['change_percent'] = f"-{percent}"
    
    except Exception as e:
        print(f"解析错误: {e}")
    
    return result

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
            content = item.get('full_content', '')
            parsed = parse_full_content(content)
            
            # 格式化涨幅显示
            change_percent = parsed['change_percent']
            if change_percent and change_percent != '-':
                try:
                    percent_val = float(change_percent)
                    if percent_val >= 0:
                        change_percent = f"+{percent_val:.2f}%"
                    else:
                        change_percent = f"{percent_val:.2f}%"
                except:
                    change_percent = f"{change_percent}%"
            else:
                change_percent = '-'
            
            # 组合商品名称
            product_name = parsed['product']
            if parsed.get('skin'):
                product_name = f"{product_name} | {parsed['skin']}"
            
            df_data.append({
                '序号': i,
                '时间': parsed['timestamp'],
                '商品': product_name,
                '磨损': parsed['wear'],
                '旧价': f"¥{parsed['old_price']}" if parsed['old_price'] else '-',
                '新价': f"¥{parsed['new_price']}" if parsed['new_price'] else '-',
                '变化': f"{parsed['old_price']} >> {parsed['new_price']}" if parsed['old_price'] and parsed['new_price'] else '-',
                '涨幅': change_percent
            })
        
        df = pd.DataFrame(df_data)
        
        # 创建图表
        import matplotlib.pyplot as plt
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
            colWidths=[0.05, 0.08, 0.2, 0.08, 0.08, 0.08, 0.15, 0.1]
        )
        
        # 设置表格样式
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        # 设置表头样式
        for i in range(len(df.columns)):
            cell = table[(0, i)]
            cell.set_facecolor('#4472C4')
            cell.set_text_props(weight='bold', color='white', fontsize=10)
            cell.set_height(0.08)
        
        # 设置行颜色和样式
        for i in range(1, len(df) + 1):
            for j in range(len(df.columns)):
                cell = table[(i, j)]
                
                # 交替行颜色
                if i % 2 == 0:
                    cell.set_facecolor('#F5F5F5')
                else:
                    cell.set_facecolor('white')
                
                cell.set_edgecolor('#CCCCCC')
                cell.set_text_props(fontsize=8)
                
                # 涨幅列加粗并着色
                if j == 7:  # 涨幅列
                    cell.set_text_props(weight='bold', fontsize=9)
                    # 根据涨幅值着色
                    try:
                        percent_str = df.iloc[i-1]['涨幅'].replace('%', '').replace('+', '')
                        percent_val = float(percent_str)
                        if percent_val > 0:
                            cell.set_text_props(weight='bold', color='#FF4444', fontsize=9)
                        elif percent_val < 0:
                            cell.set_text_props(weight='bold', color='#00AA00', fontsize=9)
                    except ValueError as e:
                        logger.debug(f"涨幅值转换失败: {e}")
                        continue
        
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
