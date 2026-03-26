import os

# 扫描根目录所有文件
root = r'E:\2026 年 KPI'
print(f'=== 根目录文件：{root} ===\n')

files = os.listdir(root)
print(f'共 {len(files)} 个项目:\n')

for f in files:
    full = os.path.join(root, f)
    if os.path.isfile(full):
        if f.endswith('.xlsx') or f.endswith('.xls') or f.endswith('.csv'):
            print(f'[数据文件] {f}')
        else:
            print(f'[文件] {f}')
    else:
        print(f'[文件夹] {f}')
