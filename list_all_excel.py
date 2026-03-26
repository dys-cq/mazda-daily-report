import os

# 精确扫描
target = r'E:\2026 年 KPI\每日分析'
print(f'Scanning: {target}\n')

# 列出所有子文件夹
for item in os.listdir(target):
    full = os.path.join(target, item)
    if os.path.isdir(full):
        print(f'Folder: {item}')
        # 列出文件夹内的所有 xlsx/xls 文件
        for f in os.listdir(full):
            if f.endswith('.xlsx') or f.endswith('.xls'):
                if not f.startswith('~$'):
                    print(f'  [XLS] {f}')
        print()
