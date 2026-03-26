import os, pandas as pd
from pprint import pprint

workspace = os.path.expanduser('~/.openclaw/workspace')

# Biz csv
biz_path = os.path.join(workspace, 'sheet_3_3月mazda.csv')
if os.path.exists(biz_path):
    biz = pd.read_csv(biz_path)
    print('=== biz cols sample ===')
    cols = biz.columns.tolist()
    keywords = ['零件','达成','台','台次','机油','事故','单车','季度','Q1','Q2','Q3','Q4']
    match = [c for c in cols if any(k in str(c) for k in keywords)]
    print(match)
    # rows for target codes
    for code in ['M18003','M23002','A28856','M18571','M18912']:
        row = biz[biz.iloc[:,0].astype(str)==code]
        if not row.empty:
            r = row.iloc[0]
            print('\n--', code, '--')
            for c in match[:40]:
                print(c, r.get(c))

# Lead/complaint
lead_file = None
base=None
for item in os.scandir('E:/'):
    if '2026' in item.name and 'KPI' in item.name and item.is_dir():
        base=item.path; break
if base:
    for sub in os.scandir(base):
        if 'ÿ' in sub.name or '每' in sub.name:
            daily=sub.path; break
    for f in os.listdir(daily):
        if '线索' in f or '客诉' in f:
            lead_file=os.path.join(daily,f); break
if lead_file:
    print('\nLead file', lead_file)
    try:
        lead = pd.read_excel(lead_file)
    except Exception:
        lead = pd.read_excel(lead_file, engine='xlrd')
    print('Lead cols:', lead.columns.tolist())
    # show rows for five codes
    for code in ['M18003','M23002','A28856','M18571','M18912']:
        mask = False
        for c in lead.columns:
            if lead[c].astype(str).str.contains(code, na=False).any():
                mask = lead[c].astype(str).str.contains(code, na=False)
                break
        if mask is not False:
            subset = lead[mask]
            print('\n--', code, 'rows--')
            print(subset.head())

# CSI
csi_file=None
if base:
    for sub in os.scandir(base):
        if 'ÿ' in sub.name or '每' in sub.name:
            daily=sub.path; break
    for f in os.listdir(daily):
        if f.lower().startswith('csi'):
            csi_file=os.path.join(daily,f); break
if csi_file:
    print('\nCSI file', csi_file)
    xl = pd.ExcelFile(csi_file)
    print('CSI sheets:', xl.sheet_names)
    # 统计表
    if '统计表' in xl.sheet_names:
        stat = pd.read_excel(csi_file, sheet_name='统计表')
        print('统计表 cols:', stat.columns.tolist())
        for code in ['M18003','M23002','A28856','M18571','M18912']:
            for c in stat.columns:
                if stat[c].astype(str).str.contains(code, na=False).any():
                    rows = stat[stat[c].astype(str).str.contains(code, na=False)]
                    print('\n--stat', code, '--')
                    print(rows.head())
                    break
    # 不满意客户清单
    for sh in xl.sheet_names:
        if '不满意' in sh:
            bm = pd.read_excel(csi_file, sheet_name=sh)
            print('\n不满意 sheet', sh, 'cols', bm.columns.tolist())
            for code in ['M18003','M23002','A28856','M18571','M18912']:
                for c in bm.columns:
                    if bm[c].astype(str).str.contains(code, na=False).any():
                        rows = bm[bm[c].astype(str).str.contains(code, na=False)]
                        print('\n--不满意', code, '--')
                        print(rows.head())
                        break
