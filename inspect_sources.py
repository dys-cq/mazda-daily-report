import os, pandas as pd
base=None
for item in os.scandir('E:/'):
    if '2026' in item.name and 'KPI' in item.name and item.is_dir():
        base=item.path; break
print('base', base)
daily=None
for sub in os.scandir(base):
    if 'ÿ' in sub.name or '每' in sub.name:
        daily=sub.path; break
print('daily', daily)

files = os.listdir(daily)
print('files', files)

# Helper to preview

def preview(path):
    print('\n===', os.path.basename(path),'===')
    try:
        xl = pd.ExcelFile(path)
        print('sheets', xl.sheet_names)
        for s in xl.sheet_names[:2]:
            df = pd.read_excel(path, sheet_name=s)
            print('sheet', s, 'shape', df.shape, 'cols', list(df.columns)[:12])
            print(df.head(3))
    except Exception as e:
        print('error', e)

# comprehensive daily
for name in files:
    if '综合日报' in name:
        preview(os.path.join(daily,name))

# platform/保险
for name in files:
    if '平台' in name or 'ƽ̨' in name:
        preview(os.path.join(daily,name))

# CSI
for name in files:
    if name.lower().startswith('csi'):
        preview(os.path.join(daily,name))

# 线索/客诉
for name in files:
    if '线索' in name or '客诉' in name:
        preview(os.path.join(daily,name))
