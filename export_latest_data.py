"""
从 E:/2026 年 KPI 目录下的最新售后日报 Excel 导出数据
同时复制保险平台线索文件到任务文件夹
"""
import os, pandas as pd, shutil
from datetime import datetime

workspace = r'C:\Users\Administrator\.openclaw\workspace'

# 查找每日分析目录和最新任务文件夹
daily_dir = None
run_folder = None
for it in os.scandir('E:/'):
    if it.is_dir() and '2026' in it.name and 'KPI' in it.name:
        for sub in os.scandir(it.path):
            if sub.is_dir() and ('每' in sub.name or 'ÿ' in sub.name):
                daily_dir = sub.path
                # 找最新的任务文件夹
                try:
                    tasks = [d.path for d in os.scandir(sub.path) if d.is_dir() and ('统计' in d.name or '重新' in d.name)]
                    if tasks:
                        tasks.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                        run_folder = tasks[0]
                except:
                    pass

# 扫描 E 盘查找最新售后日报
def find_latest_aftermarket():
    candidates=[]
    for it in os.scandir('E:/'):
        if not it.is_dir(): continue
        for root, dirs, files in os.walk(it.path):
            for f in files:
                if f.endswith('.xlsx') and not f.startswith('~$'):
                    if '售后' in f or '日报' in f:
                        full=os.path.join(root,f)
                        candidates.append((full, os.path.getmtime(full)))
    if candidates:
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    return None

# 查找保险平台文件
def find_platform_file():
    for it in os.scandir('E:/'):
        if not it.is_dir(): continue
        for root, dirs, files in os.walk(it.path):
            for f in files:
                if f.endswith('.xlsx') and '保险平台' in f and not f.startswith('~$'):
                    return os.path.join(root, f)
    return None

# 主程序
aftermarket_file = find_latest_aftermarket()
platform_file = find_platform_file()

if aftermarket_file:
    print(f'Found aftermarket: {aftermarket_file}')
    # 导出到工作区
    print(f'\nExporting aftermarket to workspace...')
    xl=pd.ExcelFile(aftermarket_file)
    for sn in xl.sheet_names:
        try:
            df=pd.read_excel(aftermarket_file, sheet_name=sn)
            safe_sn=''.join(c if c.isalnum() or c in '-_' else '_' for c in sn)
            csv_path=os.path.join(workspace, f'sheet_{safe_sn}.csv')
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f'  {sn}: {len(df)} rows')
        except Exception as e:
            print(f'  Error {sn}: {e}')
else:
    print('No aftermarket report found')

if platform_file:
    print(f'\nFound platform: {platform_file}')
    # 复制保险平台文件到工作区和 run_folder
    shutil.copy(platform_file, os.path.join(workspace, '保险平台线索.xlsx'))
    print(f'  Copied to workspace')
    if run_folder:
        shutil.copy(platform_file, os.path.join(run_folder, '保险平台线索.xlsx'))
        print(f'  Copied to run_folder')
else:
    print('\nNo platform file found')

# 复制 ALL CSV 到 run_folder
if run_folder:
    print(f'\nCopying CSV to run_folder: {run_folder}')
    count = 0
    for f in os.listdir(workspace):
        if f.startswith('sheet_') and f.endswith('.csv'):
            src = os.path.join(workspace, f)
            dst = os.path.join(run_folder, f)
            shutil.copy(src, dst)
            count += 1
    print(f'  Copied {count} CSV files')

print('\nDone!')
