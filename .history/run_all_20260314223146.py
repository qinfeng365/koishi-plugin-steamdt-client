#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SteamDT 异动数据一站式获取脚本
输入滑动次数，自动爬取、解析、生成表格图片
"""

import asyncio
import sys
import os
from datetime import datetime

async def main():
    """主函数"""
    
    # 获取滑动次数参数
    if len(sys.argv) > 1:
        try:
            max_scrolls = int(sys.argv[1])
        except ValueError:
            max_scrolls = 10
    else:
        max_scrolls = 10
    
    print("=" * 60)
    print("SteamDT CS2 饰品异动数据一站式获取工具")
    print("=" * 60)
    print(f"\n配置: 滑动次数 = {max_scrolls}")
    print()
    
    # 步骤 1: 爬取数据
    print("[1/3] 正在爬取数据...")
    print("-" * 60)
    
    from steamdt_scraper_final import SteamDTScraper
    
    scraper = SteamDTScraper(max_scrolls=max_scrolls)
    data = await scraper.run()
    
    if not data:
        print("错误: 爬取数据失败")
        return False
    
    print(f"✓ 成功爬取 {len(data)} 条数据\n")
    
    # 步骤 2: 生成表格图片
    print("[2/3] 正在生成表格图片...")
    print("-" * 60)
    
    from generate_table_image import generate_table_image
    
    # 生成表格图片（渲染所有数据）
    success = generate_table_image(
        json_file='steamdt_changes.json',
        output_file='table.png',
        rows=len(data)  # 渲染所有数据
    )
    
    if not success:
        print("错误: 生成表格图片失败")
        return False
    
    print()
    
    # 步骤 3: 生成统计信息
    print("[3/3] 生成统计信息...")
    print("-" * 60)
    
    import json
    
    # 统计数据
    up_count = sum(1 for item in data if item.get('price_trend') == '上涨')
    down_count = sum(1 for item in data if item.get('price_trend') == '下跌')
    
    # 计算平均涨幅
    valid_percents = []
    for item in data:
        try:
            percent = float(item.get('price_change_percent', 0))
            valid_percents.append(percent)
        except:
            pass
    
    avg_change = sum(valid_percents) / len(valid_percents) if valid_percents else 0
    
    # 找出最大涨幅和最大跌幅
    max_up = None
    max_up_percent = -999
    max_down = None
    max_down_percent = 999
    
    for item in data:
        try:
            percent = float(item.get('price_change_percent', 0))
            if item.get('price_trend') == '上涨' and percent > max_up_percent:
                max_up = item
                max_up_percent = percent
            elif item.get('price_trend') == '下跌' and percent < max_down_percent:
                max_down = item
                max_down_percent = percent
        except:
            pass
    
    print(f"\n📊 数据统计:")
    print(f"  总条数: {len(data)}")
    print(f"  上涨商品: {up_count}")
    print(f"  下跌商品: {down_count}")
    print(f"  平均涨幅: {avg_change:.2f}%")
    
    if max_up:
        print(f"\n  📈 最大涨幅: {max_up_percent:.2f}%")
        print(f"     {max_up.get('full_content', '')[:60]}")
    
    if max_down:
        print(f"\n  📉 最大跌幅: {max_down_percent:.2f}%")
        print(f"     {max_down.get('full_content', '')[:60]}")
    
    print()
    print("=" * 60)
    print("✓ 所有操作完成！")
    print("=" * 60)
    
    print("\n📁 生成的文件:")
    print(f"  • steamdt_changes.json - 原始数据（JSON 格式）")
    print(f"  • steamdt_changes.csv - 原始数据（CSV 格式）")
    print(f"  • table.png - 表格图片（{len(data)} 行数据）")
    print(f"  • viewer.html - 交互式查看器")
    
    print("\n🚀 查看数据:")
    print(f"  • 打开 viewer.html 在浏览器中查看")
    print(f"  • 查看 table.png 获得表格图片")
    print(f"  • 用 Excel 打开 steamdt_changes.csv")
    
    print("\n⏰ 生成时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
