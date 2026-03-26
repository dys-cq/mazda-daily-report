import os, json
import pandas as pd
from datetime import datetime

target_stores = {
    '重庆金团': 'M18003',
    '重庆瀚达': 'M23002',
    '重庆银马': 'A28856',
    '重庆万事新': 'M18571',
    '西藏鼎恒': 'M18912',
}

workspace = os.path.expanduser('~/.openclaw/workspace')
base = None
for item in os.scandir('E:/'):
    if '2026' in item.name and 'KPI' in item.name and item.is_dir():
        base = item.path; break
if not base:
    raise SystemExit('KPI path not found')

daily = None
for sub in os.scandir(base):
    if 'ÿ' in sub.name or '每' in sub.name:
        daily = sub.path; break
if not daily:
    raise SystemExit('Daily folder not found')

files = os.listdir(daily)

# Helper: safe read excel

def read_excel(path, sheet_name=0, **kw):
    try:
        return pd.read_excel(path, sheet_name=sheet_name, **kw)
    except Exception as e:
        return None

# Dealer map from existing csv
map_path = os.path.join(workspace, 'sheet_9_Sheet3.csv')
if os.path.exists(map_path):
    dealer_map = pd.read_csv(map_path)
else:
    dealer_map = pd.DataFrame()

# 经营数据 from sheet_3_3月mazda.csv if exists else from excel
mazda_csv = os.path.join(workspace, 'sheet_3_3月mazda.csv')
if os.path.exists(mazda_csv):
    mazda_df = pd.read_csv(mazda_csv)
else:
    # fallback to excel
    main_excel = [f for f in files if '综合日报' in f]
    if main_excel:
        path = os.path.join(daily, main_excel[0])
        xl = pd.ExcelFile(path)
        sheet_name = [s for s in xl.sheet_names if '3' in s][0]
        mazda_df = pd.read_excel(path, sheet_name=sheet_name)
    else:
        mazda_df = pd.DataFrame()

# 平台/保险数据
platform_file = None
for f in files:
    if '平台' in f or 'ƽ̨' in f:
        platform_file = os.path.join(daily, f); break
platform_df = None
if platform_file:
    try:
        platform_df = pd.read_excel(platform_file, sheet_name=0)
    except Exception:
        platform_df = None

# CSI 数据
csi_file = None
for f in files:
    if f.lower().startswith('csi'):
        csi_file = os.path.join(daily, f); break
csi_df = None
if csi_file:
    try:
        csi_df = pd.read_excel(csi_file, sheet_name=1)  # second sheet has raw
    except Exception:
        try:
            csi_df = pd.read_excel(csi_file, sheet_name=0)
        except Exception:
            csi_df = None

# 客诉/线索
lead_file = None
for f in files:
    if '线索' in f or '客诉' in f:
        lead_file = os.path.join(daily, f); break
lead_df = None
if lead_file:
    try:
        lead_df = pd.read_excel(lead_file, engine='xlrd')
    except Exception:
        try:
            lead_df = pd.read_excel(lead_file)
        except Exception:
            lead_df = None

# Extract metrics per store
store_rows = {}
for name, code in target_stores.items():
    # 经营
    biz_row = None
    if not mazda_df.empty:
        col_code = mazda_df.columns[0]
        m = mazda_df[mazda_df[col_code].astype(str)==code]
        if not m.empty:
            biz_row = m.iloc[0]
    # 平台
    plat_row = None
    if platform_df is not None and not platform_df.empty:
        # find code column
        code_col = None
        for c in platform_df.columns:
            if '代码' in str(c) or '�' in str(c):
                code_col = c; break
        if code_col:
            mm = platform_df[platform_df[code_col].astype(str)==code]
            if not mm.empty:
                plat_row = mm.iloc[0]
    # CSI
    csi_row = None
    if csi_df is not None and not csi_df.empty:
        for c in csi_df.columns:
            if '经销商' in str(c) or '代码' in str(c) or '4S' in str(c):
                mm = csi_df[csi_df[c].astype(str).str.contains(code, na=False)]
                if not mm.empty:
                    csi_row = mm.iloc[0]
                    break
    # 客诉/线索
    lead_row = None
    if lead_df is not None and not lead_df.empty:
        for c in lead_df.columns:
            if '经销商' in str(c) or '代码' in str(c) or '4S' in str(c):
                mm = lead_df[lead_df[c].astype(str).str.contains(code, na=False)]
                if not mm.empty:
                    lead_row = mm.iloc[0]
                    break
    store_rows[name] = {
        'biz': biz_row,
        'platform': plat_row,
        'csi': csi_row,
        'lead': lead_row,
    }

# build markdown
report_date = '2026-03-10'
md = []
md.append(f"# KPI 每日全维度分析报告\n\n**报告日期**: {report_date}  ")
md.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n")
md.append("## 目标店铺\n")
md.append("| 店铺 | 代码 |\n|---|---|")
for k,v in target_stores.items():
    md.append(f"| {k} | {v} |")
md.append("\n---\n")

for store in target_stores.keys():
    md.append(f"## {store}\n")
    rows = store_rows[store]
    # 经营
    md.append("### 经营（日常）")
    if rows['biz'] is not None:
        r = rows['biz']
        def gv(col):
            return r[col] if col in r.index else None
        metrics = {
            '服务总收入': gv('服务总收入') or gv('服务收入') or gv('服务总收入 '),
            '零件总收入': gv('零件总收入'),
            '工时总收入': gv('工时总收入'),
            '普通维修产值': gv('普通维修产值小计'),
            '事故维修产值': gv('事故维修产值小计'),
            '进店批次': gv('进店批次') or gv('进店台次') or gv('进店批次 '),
            '成交批次': gv('成交批次') or gv('成交台次'),
        }
        md.append('| 指标 | 数值 |'); md.append('|---|---|')
        for k,v in metrics.items():
            if v is not None:
                md.append(f"| {k} | {v:,} |")
    else:
        md.append('（暂无经营数据）')
    # 平台/保险
    md.append("\n### 保险/平台线索")
    if rows['platform'] is not None:
        p=rows['platform']
        md.append('| 指标 | 数值 |'); md.append('|---|---|')
        for col in p.index[:10]:
            md.append(f"| {col} | {p[col]} |")
    else:
        md.append('（暂无平台数据）')
    # 客诉/线索
    md.append("\n### 客诉/线索")
    if rows['lead'] is not None:
        l=rows['lead']
        md.append('| 字段 | 值 |'); md.append('|---|---|')
        for col in l.index[:8]:
            md.append(f"| {col} | {l[col]} |")
    else:
        md.append('（暂无客诉/线索数据）')
    # CSI
    md.append("\n### CSI 自主调研")
    if rows['csi'] is not None:
        c=rows['csi']
        md.append('| 字段 | 值 |'); md.append('|---|---|')
        for col in c.index[:8]:
            md.append(f"| {col} | {c[col]} |")
    else:
        md.append('（暂无 CSI 数据）')
    md.append('\n---\n')

md_text='\n'.join(md)
md_path=os.path.join(workspace,'KPI 日报_20260310_full.md')
with open(md_path,'w',encoding='utf-8') as f:
    f.write(md_text)
print('MD written', md_path)

# simple HTML from md
html_path=os.path.join(workspace,'KPI 日报_20260310_full.html')
html = f"<html><head><meta charset='utf-8'><title>KPI 全维度报告</title></head><body><pre>{md_text}</pre></body></html>"
with open(html_path,'w',encoding='utf-8') as f:
    f.write(html)
print('HTML written', html_path)
