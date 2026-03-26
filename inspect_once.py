import os, pandas as pd
# locate daily folder
base=None
for item in os.scandir('E:/'):
    if '2026' in item.name and 'KPI' in item.name and item.is_dir():
        base=item.path; break
for sub in os.scandir(base):
    if 'ÿ' in sub.name or '每' in sub.name:
        daily=sub.path; break
files=os.listdir(daily)
lead_file=None
csi_file=None
for f in files:
    if '线索' in f or '客诉' in f:
        lead_file=os.path.join(daily,f)
    if f.lower().startswith('csi'):
        csi_file=os.path.join(daily,f)
print('lead_file', lead_file)
print('csi_file', csi_file)

# inspect lead tables
if lead_file:
    try:
        tables=pd.read_html(lead_file)
        print('lead tables count', len(tables))
        for i,t in enumerate(tables[:3]):
            print('\nTable', i, 'shape', t.shape)
            print(t.head())
            print('Cols:', list(t.columns))
    except Exception as e:
        print('lead read_html error', e)

# inspect csi
if csi_file:
    xl=pd.ExcelFile(csi_file)
    print('CSI sheets', xl.sheet_names)
    if '统计表' in xl.sheet_names:
        stat=pd.read_excel(csi_file, sheet_name='统计表')
        print('\nCSI 统计表 cols:', list(stat.columns))
        print(stat.head())
    for s in xl.sheet_names:
        if '不满意' in s:
            bm=pd.read_excel(csi_file, sheet_name=s)
            print('\n不满意 sheet', s, 'cols', list(bm.columns))
            print(bm.head())
            break
