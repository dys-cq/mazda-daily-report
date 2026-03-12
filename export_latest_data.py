"""
从 E:/2026 年 KPI 目录下的最新售后日报 Excel 导出数据到工作区
"""
import os, pandas as pd, shutil
from datetime import datetime

workspace = r'C:\Users\Administrator\.openclaw\workspace'

# 直接扫描 E 盘查找售后日报
def find_latest_aftermarket():
    candidates=[]
    for it in os.scandir('E:/'):
        if not it.is_dir():
            continue
        for root, dirs, files in os.walk(it.path):
            for f in files:
                if f.endswith('.xlsx') and not f.startswith('~$'):
                    # 检查是否包含"售后"或"日报"
                    if '售后' in f or '日报' in f:
                        full=os.path.join(root,f)
                        candidates.append((full, os.path.getmtime(full)))
    if candidates:
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    return None

def export_sheets_to_csv(xls_file, output_dir):
    """将 Excel 的多个 sheet 导出为 CSV"""
    xl=pd.ExcelFile(xls_file)
    exported=[]
    for sn in xl.sheet_names:
        try:
            df=pd.read_excel(xls_file, sheet_name=sn)
            safe_sn=''.join(c if c.isalnum() or c in '-_' else '_' for c in sn)
            csv_path=os.path.join(output_dir, f'sheet_{safe_sn}.csv')
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            exported.append(csv_path)
            print(f'Exported: {csv_path} ({len(df)} rows)')
        except Exception as e:
            print(f'Error exporting {sn}: {e}')
    return exported

# 主程序
aftermarket_file = find_latest_aftermarket()
if aftermarket_file:
    print(f'Found latest aftermarket report: {aftermarket_file}')
    print(f'Modified: {datetime.fromtimestamp(os.path.getmtime(aftermarket_file))}')
    
    # 导出所有 sheet 到工作区
    exported = export_sheets_to_csv(aftermarket_file, workspace)
    print(f'\nExported {len(exported)} sheets to CSV')
    
    # 重命名关键文件为脚本期望的名称
    for csv in exported:
        fname=os.path.basename(csv)
        if '零附件' in fname or '附件' in fname:
            new_name='sheet_2_零附件 - 零附件明细.csv'
            new_path=os.path.join(workspace, new_name)
            shutil.copy(csv, new_path)
            print(f'Copied to: {new_name}')
        elif '3 月' in fname or 'mazda' in fname.lower() or 'sheet_3' in fname or '综合' in fname:
            new_name='sheet_3_3 月 mazda.csv'
            new_path=os.path.join(workspace, new_name)
            shutil.copy(csv, new_path)
            print(f'Copied to: {new_name}')
else:
    print('No aftermarket report found')
