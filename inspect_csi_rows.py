import os, pandas as pd
codes=['M18003','M23002','A28856','M18571','M18912']
base=None
for it in os.scandir('E:/'):
    if '2026' in it.name and 'KPI' in it.name and it.is_dir():
        base=it.path;break
for sub in os.scandir(base):
    if 'ÿ' in sub.name or '每' in sub.name:
        daily=sub.path;break
csi=None
for f in os.listdir(daily):
    if f.lower().startswith('csi'):
        csi=os.path.join(daily,f);break
print(csi)
xl=pd.ExcelFile(csi)
print(xl.sheet_names)
stat=pd.read_excel(csi,sheet_name=0)
print('cols',list(stat.columns))
for code in codes:
    row=stat[stat.iloc[:,0].astype(str)==code]
    print('\n',code,'rows',len(row))
    if not row.empty:
        r=row.iloc[0]
        print(r.to_dict())
# dissatisfied sheet last
bad=pd.read_excel(csi,sheet_name=xl.sheet_names[-1])
print('bad cols',list(bad.columns))
for code in codes:
    m=bad[bad.iloc[:,3].astype(str)==code] if bad.shape[1]>3 else bad.iloc[0:0]
    print('bad',code,len(m))
