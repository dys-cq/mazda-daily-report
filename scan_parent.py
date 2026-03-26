import os

# 扫描父目录
parent = r'E:\2026 年 KPI'
print(f'Scanning: {parent}\n')

for item in os.listdir(parent):
    full = os.path.join(parent, item)
    if os.path.isfile(full):
        if item.endswith('.xlsx') or item.endswith('.xls'):
            if not item.startswith('~$'):
                print(f'[FILE] {item}')
    elif os.path.isdir(full):
        print(f'[DIR] {item}')
        # 检查目录内的 xlsx 文件
        try:
            for f in os.listdir(full):
                if f.endswith('.xlsx') or f.endswith('.xls'):
                    if not f.startswith('~$'):
                        print(f'  -> {f}')
        except:
            pass
