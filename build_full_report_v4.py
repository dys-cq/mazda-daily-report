import os, pandas as pd
from datetime import datetime

stores = {
    '重庆金团': 'M18003',
    '重庆瀚达': 'M23002',
    '重庆银马': 'A28856',
    '重庆万事新': 'M18571',
    '西藏鼎恒': 'M18912',
}
workspace = os.path.expanduser('~/.openclaw/workspace')

# locate paths
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
files=os.listdir(daily)

# biz
biz_df=pd.read_csv(os.path.join(workspace,'sheet_3_3月mazda.csv')) if os.path.exists(os.path.join(workspace,'sheet_3_3月mazda.csv')) else None
# platform
platform_df=None
for f in files:
    if '平台' in f or 'ƽ̨' in f:
        try:
            platform_df=pd.read_excel(os.path.join(daily,f), sheet_name=0)
        except Exception:
            platform_df=None
        break
# lead (gb18030)
lead_df=None
for f in files:
    if '线索' in f or '客诉' in f:
        path=os.path.join(daily,f)
        try:
            tables=pd.read_html(path, encoding='gb18030')
        except Exception:
            tables=pd.read_html(path)
        lead_df=max(tables, key=lambda t: t.shape[1])
        # header row
        lead_df.columns=lead_df.iloc[0]
        lead_df=lead_df.iloc[1:]
        break
# CSI
csi_stat=None; csi_bad=None
for f in files:
    if f.lower().startswith('csi'):
        path=os.path.join(daily,f)
        xl=pd.ExcelFile(path)
        # sheet0 as stat
        csi_stat=pd.read_excel(path, sheet_name=0)
        # find bad sheet
        bad_sheets=[s for s in xl.sheet_names if '��' in s or '客户' in s or '满意' in s or '嵥' in s]
        if bad_sheets:
            try:
                csi_bad=pd.read_excel(path, sheet_name=bad_sheets[-1])
            except Exception:
                csi_bad=None
        break

# helper functions
def pick_col(cols, kw_any):
    for c in cols:
        sc=str(c)
        if any(k in sc for k in kw_any):
            return c
    return None

summary={}
for store, code in stores.items():
    entry={}
    # biz
    if biz_df is not None:
        code_col=biz_df.columns[0]
        row=biz_df[biz_df[code_col].astype(str)==code]
        entry['biz']=row.iloc[0] if not row.empty else None
    else:
        entry['biz']=None
    # platform
    plat=None
    if platform_df is not None:
        code_col=pick_col(platform_df.columns, ['代码','代'])
        if code_col:
            row=platform_df[platform_df[code_col].astype(str)==code]
            plat=row.iloc[0] if not row.empty else None
    entry['platform']=plat
    # lead
    ldf=None
    if lead_df is not None:
        store_col=pick_col(lead_df.columns, ['经销','店','简称'])
        status_col=pick_col(lead_df.columns, ['状态'])
        timeout_col=pick_col(lead_df.columns, ['超时','处理'])
        if store_col:
            mask=lead_df[store_col].astype(str).str.contains(store, na=False)
            ldf=lead_df[mask]
            total=len(ldf)
            if status_col:
                unclosed=ldf[ldf[status_col].astype(str).str.contains('未', na=False)].shape[0]
                closed=ldf[ldf[status_col].astype(str).str.contains('已', na=False)].shape[0]
            else:
                unclosed=closed=0
            if timeout_col:
                timeout=(pd.to_numeric(ldf[timeout_col].astype(str).str.extract(r'(\d+)', expand=False), errors='coerce').fillna(0) > 0).sum()
            else:
                timeout=0
            entry['lead']={'total':total,'unclosed':unclosed,'closed':closed,'timeout':timeout,'sample':ldf.head(2)}
        else:
            entry['lead']=None
    else:
        entry['lead']=None
    # csi stat
    cstat=None
    if csi_stat is not None:
        code_col=pick_col(csi_stat.columns, ['代码','经销','店']) or csi_stat.columns[0]
        rows=csi_stat[csi_stat[code_col].astype(str).str.contains(code, na=False)]
        if not rows.empty:
            r=rows.iloc[0]
            # pick key cols
            keep={}
            for k in r.index:
                if any(x in str(k) for x in ['维修','合同','评价','参与','满意','率']):
                    keep[k]=r[k]
            cstat=keep
    entry['csi_stat']=cstat
    # csi bad
    cbad=None
    if csi_bad is not None:
        for c in csi_bad.columns:
            if csi_bad[c].astype(str).str.contains(code, na=False).any():
                rows=csi_bad[csi_bad[c].astype(str).str.contains(code, na=False)]
                if not rows.empty:
                    cbad=rows
                    break
    entry['csi_bad']=cbad
    summary[store]=entry

# build markdown
report_date='2026-03-10'
md=[]
md.append(f"# KPI 每日全维度分析报告\n\n**报告日期**: {report_date}  \n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n")
md.append('| 店铺 | 代码 |'); md.append('|---|---|')
for k,v in stores.items():
    md.append(f"| {k} | {v} |")
md.append('\n---\n')

for store in stores:
    s=summary[store]; md.append(f"## {store}\n")
    # biz
    md.append('### 经营（日常）')
    if s['biz'] is not None:
        r=s['biz']; cols=r.index
        def anyv(keys):
            for c in cols:
                if any(k in str(c) for k in keys):
                    return r[c]
            return None
        metrics={
            '服务总收入': anyv(['服务总']),
            '零件总收入': anyv(['零件总']),
            '工时总收入': anyv(['工时总']),
            '普通维修产值': anyv(['普通维修产值']),
            '事故维修产值': anyv(['事故维修产值']),
            '进店台次': anyv(['进店','台次']),
            '成交台次': anyv(['成交台次','成交批次']),
            '零件达成率': anyv(['零件','达成']),
            '台次达成率': anyv(['台次','达成']),
            '机油单车': anyv(['机油','单车']),
            '事故单车': anyv(['事故','单车']),
            'Q1累计零件': anyv(['Q1']),
        }
        md.append('| 指标 | 数值 |'); md.append('|---|---|')
        for k,v in metrics.items():
            if v is not None and str(v)!='nan':
                md.append(f"| {k} | {v} |")
    else:
        md.append('（无经营数据）')
    # platform
    md.append('\n### 保险/平台线索')
    if s['platform'] is not None:
        p=s['platform']; md.append('| 指标 | 数值 |'); md.append('|---|---|')
        for c in p.index[:12]:
            md.append(f"| {c} | {p[c]} |")
    else:
        md.append('（无平台数据）')
    # lead
    md.append('\n### 客诉/线索')
    if s['lead'] is not None:
        info=s['lead']; md.append(f"- 总数: {info['total']}\n- 未关闭: {info['unclosed']}\n- 已关闭: {info['closed']}\n- 超时>0: {info['timeout']}")
        md.append('| 字段 | 示例 |'); md.append('|---|---|')
        sample=info['sample']
        for c in sample.columns[:4]:
            md.append(f"| {c} | {sample.iloc[0][c]} |")
    else:
        md.append('（无客诉/线索数据）')
    # CSI
    md.append('\n### CSI 自主调研')
    if s['csi_stat']:
        md.append('| 指标 | 数值 |'); md.append('|---|---|')
        for k,v in s['csi_stat'].items():
            md.append(f"| {k} | {v} |")
    else:
        md.append('（无 CSI 统计数据）')
    md.append('\n#### 不满意客户')
    if s['csi_bad'] is not None:
        bad=s['csi_bad']; md.append(f"- 不满意客户数: {len(bad)}")
        md.append('| 字段 | 示例 |'); md.append('|---|---|')
        for c in bad.columns[:6]:
            md.append(f"| {c} | {bad.iloc[0][c]} |")
    else:
        md.append('（无不满意客户）')
    md.append('\n---\n')

md_text='\n'.join(md)
md_path=os.path.join(workspace,'KPI 日报_20260310_full.md')
with open(md_path,'w',encoding='utf-8') as f:
    f.write(md_text)
print('MD written', md_path)

html_path=os.path.join(workspace,'KPI 日报_20260310_full.html')
html=f"<html><head><meta charset='utf-8'><title>KPI 全维度报告</title></head><body><pre>{md_text}</pre></body></html>"
with open(html_path,'w',encoding='utf-8') as f:
    f.write(html)
print('HTML written', html_path)
