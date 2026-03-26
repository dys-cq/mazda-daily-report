import os, pandas as pd, json
from datetime import datetime

stores = {
    '重庆金团': 'M18003',
    '重庆瀚达': 'M23002',
    '重庆银马': 'A28856',
    '重庆万事新': 'M18571',
    '西藏鼎恒': 'M18912',
}

workspace = os.path.expanduser('~/.openclaw/workspace')

# find base and daily
base=None
for item in os.scandir('E:/'):
    if '2026' in item.name and 'KPI' in item.name and item.is_dir():
        base=item.path; break
if not base:
    raise SystemExit('base not found')
daily=None
for sub in os.scandir(base):
    if 'ÿ' in sub.name or '每' in sub.name:
        daily=sub.path; break
if not daily:
    raise SystemExit('daily not found')
files=os.listdir(daily)

# dealer map
map_path=os.path.join(workspace,'sheet_9_Sheet3.csv')
dealer_map=pd.read_csv(map_path) if os.path.exists(map_path) else pd.DataFrame()

# business data
biz_df=None
biz_csv=os.path.join(workspace,'sheet_3_3月mazda.csv')
if os.path.exists(biz_csv):
    biz_df=pd.read_csv(biz_csv)
else:
    for f in files:
        if '综合日报' in f:
            path=os.path.join(daily,f)
            xl=pd.ExcelFile(path)
            sheet=[s for s in xl.sheet_names if '3' in s][0]
            biz_df=pd.read_excel(path, sheet_name=sheet)
            break

# platform data
platform_df=None
for f in files:
    if '平台' in f or 'ƽ̨' in f:
        try:
            platform_df=pd.read_excel(os.path.join(daily,f), sheet_name=0)
        except Exception:
            platform_df=None
        break

# CSI data
csi_stat=None; csi_bad=None
for f in files:
    if f.lower().startswith('csi'):
        path=os.path.join(daily,f)
        xl=pd.ExcelFile(path)
        if '统计表' in xl.sheet_names:
            csi_stat=pd.read_excel(path, sheet_name='统计表')
        bad_sheets=[s for s in xl.sheet_names if '不满意' in s]
        if bad_sheets:
            csi_bad=pd.read_excel(path, sheet_name=bad_sheets[0])
        break

# lead/complaint data (html disguised xls)
lead_df=None
for f in files:
    if '线索' in f or '客诉' in f:
        path=os.path.join(daily,f)
        try:
            tables=pd.read_html(path)
            # pick widest table
            lead_df=max(tables, key=lambda t: t.shape[1])
        except Exception:
            lead_df=None
        break

# helper to pick first matching column

def pick_col(cols, keywords):
    for c in cols:
        sc=str(c)
        if all(k in sc for k in keywords):
            return c
    for c in cols:
        sc=str(c)
        if any(k in sc for k in keywords):
            return c
    return None

summary={}
for store, code in stores.items():
    entry={}
    # biz row
    if biz_df is not None and not biz_df.empty:
        code_col=biz_df.columns[0]
        row=biz_df[biz_df[code_col].astype(str)==code]
        entry['biz']=row.iloc[0] if not row.empty else None
    else:
        entry['biz']=None
    # platform row
    plat=None
    if platform_df is not None:
        code_col=None
        for c in platform_df.columns:
            if '代码' in str(c) or '代' in str(c):
                code_col=c; break
        if code_col:
            r=platform_df[platform_df[code_col].astype(str)==code]
            plat=r.iloc[0] if not r.empty else None
    entry['platform']=plat
    # lead subset
    ldf=None
    if lead_df is not None:
        mask=None
        for c in lead_df.columns:
            if lead_df[c].astype(str).str.contains(code, na=False).any():
                mask=lead_df[c].astype(str).str.contains(code, na=False)
                break
        if mask is not None:
            ldf=lead_df[mask]
    entry['lead']=ldf
    # csi stat subset
    cstat=None
    if csi_stat is not None:
        mask=None
        for c in csi_stat.columns:
            if csi_stat[c].astype(str).str.contains(code, na=False).any():
                mask=csi_stat[c].astype(str).str.contains(code, na=False)
                break
        if mask is not None:
            cstat=csi_stat[mask]
    entry['csi_stat']=cstat
    # csi bad
    cbad=None
    if csi_bad is not None:
        mask=None
        for c in csi_bad.columns:
            if csi_bad[c].astype(str).str.contains(code, na=False).any():
                mask=csi_bad[c].astype(str).str.contains(code, na=False)
                break
        if mask is not None:
            cbad=csi_bad[mask]
    entry['csi_bad']=cbad
    summary[store]=entry

# build markdown lines
report_date='2026-03-10'
md=[]
md.append(f"# KPI 每日全维度分析报告\n\n**报告日期**: {report_date}  \n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n")
md.append('| 店铺 | 代码 |'); md.append('|---|---|')
for k,v in stores.items():
    md.append(f"| {k} | {v} |")
md.append('\n---\n')

for store in stores:
    code=stores[store]
    s=summary[store]
    md.append(f"## {store}\n")
    # 经营
    md.append('### 经营（日常）')
    if s['biz'] is not None:
        r=s['biz']
        metrics={}
        cols=r.index
        def find(keys):
            return next((r[c] for c in cols if all(k in str(c) for k in keys)), None)
        def find_any(keys):
            return next((r[c] for c in cols if any(k in str(c) for k in keys)), None)
        metrics['服务总收入']=find_any(['服务总'])
        metrics['零件总收入']=find_any(['零件总'])
        metrics['工时总收入']=find_any(['工时总'])
        metrics['普通维修产值']=find_any(['普通维修产值'])
        metrics['事故维修产值']=find_any(['事故维修产值'])
        metrics['进店台次']=find_any(['进店','台次'])
        metrics['成交台次']=find_any(['成交台次','成交批次'])
        metrics['零件达成率']=find_any(['零件','达成'])
        metrics['台次达成率']=find_any(['台次','达成'])
        metrics['机油单车']=find_any(['机油','单车'])
        metrics['事故单车']=find_any(['事故','单车'])
        metrics['Q1累计零件']=find_any(['Q1'])
        md.append('| 指标 | 数值 |'); md.append('|---|---|')
        for k,v in metrics.items():
            if v is not None and str(v)!='nan':
                md.append(f"| {k} | {v} |")
    else:
        md.append('（无经营数据）')
    # 平台
    md.append('\n### 保险/平台线索')
    if s['platform'] is not None:
        p=s['platform']
        md.append('| 指标 | 数值 |'); md.append('|---|---|')
        for c in p.index[:12]:
            md.append(f"| {c} | {p[c]} |")
    else:
        md.append('（无平台数据）')
    # 客诉/线索
    md.append('\n### 客诉/线索')
    if s['lead'] is not None and not s['lead'].empty:
        df=s['lead']
        total=len(df)
        unclosed=0; closed=0; timeout=0
        status_col=pick_col(df.columns,['状态']) or pick_col(df.columns,['关闭'])
        if status_col:
            unclosed=df[df[status_col].astype(str).str.contains('未',na=False)].shape[0]
            closed=df[df[status_col].astype(str).str.contains('已',na=False)].shape[0]
        timeout_col=pick_col(df.columns,['超时']) or pick_col(df.columns,['处理'])
        if timeout_col:
            try:
                timeout=(pd.to_numeric(df[timeout_col], errors='coerce').fillna(0) > 0).sum()
            except Exception:
                timeout=0
        md.append(f"- 客诉/线索总数: {total}\n- 未关闭: {unclosed}\n- 已关闭: {closed}\n- 超时时长>0: {timeout}")
        md.append('| 字段 | 示例值 |'); md.append('|---|---|')
        sample_cols=df.columns[:4]
        for c in sample_cols:
            md.append(f"| {c} | {df.iloc[0][c]} |")
    else:
        md.append('（无客诉/线索数据）')
    # CSI
    md.append('\n### CSI 自主调研')
    if s['csi_stat'] is not None and not s['csi_stat'].empty:
        cs=s['csi_stat']; r=cs.iloc[0]
        md.append('| 指标 | 数值 |'); md.append('|---|---|')
        for k in r.index:
            if any(x in str(k) for x in ['维修合同','评价','参与率','满意','满意率']):
                md.append(f"| {k} | {r[k]} |")
    else:
        md.append('（无 CSI 统计数据）')
    md.append('\n#### 不满意客户')
    if s['csi_bad'] is not None and not s['csi_bad'].empty:
        bad=s['csi_bad']
        md.append(f"- 不满意客户数: {len(bad)}")
        show_cols=bad.columns[:6]
        md.append('| 字段 | 示例 |'); md.append('|---|---|')
        for c in show_cols:
            md.append(f"| {c} | {bad.iloc[0][c]} |")
    else:
        md.append('（无不满意客户）')
    md.append('\n---\n')

md_text='\n'.join(md)
md_path=os.path.join(workspace,'KPI 日报_20260310_full.md')
with open(md_path,'w',encoding='utf-8') as f:
    f.write(md_text)
print('MD written', md_path)

# HTML with Chart.js basic
html_path=os.path.join(workspace,'KPI 日报_20260310_full.html')
html=f"""<!doctype html><html><head><meta charset='utf-8'><title>KPI 全维度报告</title>
<script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
<style>body{{font-family:'Microsoft YaHei',Arial;padding:20px;background:#f5f6fa;}}.card{{background:#fff;padding:20px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.08);margin-bottom:20px;}}</style></head><body>
<h1>KPI 每日全维度报告</h1><p>报告日期 {report_date} | 生成 {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
<div class='card'><pre>{md_text}</pre></div>
</body></html>"""
with open(html_path,'w',encoding='utf-8') as f:
    f.write(html)
print('HTML written', html_path)
