import os, pandas as pd
stores=['重庆金团','重庆瀚达','重庆银马','重庆万事新','西藏鼎恒']
base=None
for it in os.scandir('E:/'):
    if '2026' in it.name and 'KPI' in it.name and it.is_dir():
        base=it.path;break
for sub in os.scandir(base):
    if 'ÿ' in sub.name or '每' in sub.name:
        daily=sub.path;break
lead=None
for f in os.listdir(daily):
    if '线索' in f or '客诉' in f:
        lead=os.path.join(daily,f);break
print('lead',lead)
# try utf-8 then gb18030
try:
    tables=pd.read_html(lead,encoding='utf-8')
except Exception:
    tables=pd.read_html(lead,encoding='gb18030')
df=max(tables,key=lambda t:t.shape[1])
df.columns=df.iloc[0]
df=df.iloc[1:]
print('cols:',list(df.columns))
# guess cols
name_col=None
status_col=None
timeout_col=None
for c in df.columns:
    s=str(c)
    if ('经销' in s and '简称' in s) or ('经销' in s):
        name_col=c
    if '状态' in s:
        status_col=c
    if '超时' in s:
        timeout_col=c
print('name_col',name_col,'status_col',status_col,'timeout_col',timeout_col)
if name_col is None:
    name_col=df.columns[15]
if status_col is None:
    status_col=df.columns[8]
if timeout_col is None:
    timeout_col=df.columns[-1]

for st in stores:
    sub=df[df[name_col].astype(str).str.contains(st,na=False)]
    total=len(sub)
    closed=sub[sub[status_col].astype(str).str.contains('关闭|已',na=False)].shape[0]
    unclosed=sub[sub[status_col].astype(str).str.contains('未',na=False)].shape[0]
    timeout=(pd.to_numeric(sub[timeout_col].astype(str).str.extract(r'(\d+)',expand=False),errors='coerce').fillna(0)>0).sum()
    print(st,total,closed,unclosed,timeout)
    if total:
        print(sub[[name_col,status_col,timeout_col]].head())
