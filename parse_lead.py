import os, pandas as pd
# locate lead file
base=None
for item in os.scandir('E:/'):
    if '2026' in item.name and 'KPI' in item.name and item.is_dir():
        base=item.path; break
if not base: raise SystemExit('base not found')
daily=None
for sub in os.scandir(base):
    if 'ÿ' in sub.name or '每' in sub.name:
        daily=sub.path; break
if not daily: raise SystemExit('daily not found')
lead=None
for f in os.listdir(daily):
    if '线索' in f or '客诉' in f:
        lead=os.path.join(daily,f); break
if not lead: raise SystemExit('lead not found')
print('lead file:', lead)
# read html disguised
try:
    tables = pd.read_html(lead, encoding='utf-8')
except Exception as e:
    print('read_html failed utf-8', e)
    try:
        tables = pd.read_html(lead, encoding='gb18030')
    except Exception as e2:
        print('read_html failed gb18030', e2)
        raise
print('table count', len(tables))
# pick widest
tbl = max(tables, key=lambda t: t.shape[1])
print('picked table shape', tbl.shape)
print('columns:', list(tbl.columns))
print(tbl.head(5))
# if first row is header
if tbl.iloc[0].isnull().sum()==0:
    tbl2 = tbl.copy()
    tbl2.columns = tbl2.iloc[0]
    tbl2 = tbl2.iloc[1:]
    print('\nafter header reset:')
    print('columns:', list(tbl2.columns))
    print(tbl2.head(5))
