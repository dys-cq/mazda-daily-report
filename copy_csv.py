import os, shutil
workspace = r'C:\Users\Administrator\.openclaw\workspace'
run_folder = r'E:/2026 年 KPI/每日分析/2026-03-11-重新统计'
count = 0
for f in os.listdir(workspace):
    if f.startswith('sheet_') and f.endswith('.csv'):
        src = os.path.join(workspace, f)
        dst = os.path.join(run_folder, f)
        shutil.copy(src, dst)
        count += 1
print(f'Copied {count} files')
print(f'Files in run_folder: {os.listdir(run_folder)[:10]}')
