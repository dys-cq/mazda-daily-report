"""
一键生成 KPI 日报
1. 从 E:/2026 年 KPI 导出最新售后日报数据
2. 生成完整的 KPI 日报（HTML + Markdown）
"""
import subprocess, sys

print('='*60)
print('Step 1: 导出最新售后日报数据...')
print('='*60)
result = subprocess.run([sys.executable, 'export_latest_data.py'], capture_output=False)
if result.returncode != 0:
    print('导出失败！')
    sys.exit(1)

print()
print('='*60)
print('Step 2: 生成 KPI 日报...')
print('='*60)
result = subprocess.run([sys.executable, 'build_final_report_v7.py'], capture_output=False)
if result.returncode != 0:
    print('报表生成失败！')
    sys.exit(1)

print()
print('='*60)
print('✅ 完成！报表已生成到 E:/2026 年 KPI/每日分析/ 目录')
print('='*60)
