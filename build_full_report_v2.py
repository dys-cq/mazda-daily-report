import os, pandas as pd, json
from datetime import datetime

# target stores and codes
stores = {
    '重庆金团': 'M18003',
    '重庆瀚达': 'M23002',
    '重庆银马': 'A28856',
    '重庆万事新': 'M18571',
    '西藏鼎恒': 'M18912',
}

workspace = os.path.expanduser('~/.openclaw/workspace')

# locate daily folder
base=None
for item in os.scandir('E:/'):
    if '2026' in item.name and 'KPI' in item.name and item.is_dir():
        base=item.path; break
if not base:
    raise SystemExit('KPI path not found')
daily=None
for sub in os.scandir(base):
    if 'ÿ' in sub.name or '每' in sub.name:
        daily=sub.path; break
if not daily:
    raise SystemExit('daily path not found')

files=os.listdir(daily)

# helper to load lead via html
lead_df=None
lead_file=None
for f in files:
    if '线索' in f or '客诉' in f:
        lead_file=os.path.join(daily,f); break
if lead_file:
    try:
        lead_tables=pd.read_html(lead_file)
        lead_df=max(lead_tables, key=lambda df: df.shape[1])  # pick widest table
    except Exception as e:
        lead_df=None

# platform
platform_df=None
for f in files:
    if '平台' in f or 'ƽ̨' in f:
        path=os.path.join(daily,f)
        try:
            platform_df=pd.read_excel(path, sheet_name=0)
        except Exception:
            platform_df=None
        break

# business
biz_df=None
biz_csv=os.path.join(workspace,'sheet_3_3月mazda.csv')
if os.path.exists(biz_csv):
    biz_df=pd.read_csv(biz_csv)
else:
    for f in files:
        if '综合日报' in f:
            path=os.path.join(daily,f)
            try:
                xl=pd.ExcelFile(path)
                sheet=[s for s in xl.sheet_names if '3' in s][0]
                biz_df=pd.read_excel(path,sheet_name=sheet)
            except Exception:
                pass
            break

# CSI
csi_stat=None; csi_bad=None
for f in files:
    if f.lower().startswith('csi'):
        path=os.path.join(daily,f)
        xl=pd.ExcelFile(path)
        if '统计表' in xl.sheet_names:
            csi_stat=pd.read_excel(path, sheet_name='统计表')
        if any('不满意' in s for s in xl.sheet_names):
            sh=[s for s in xl.sheet_names if '不满意' in s][0]
            csi_bad=pd.read_excel(path, sheet_name=sh)
        break

# dealer map
map_path=os.path.join(workspace,'sheet_9_Sheet3.csv')
dealer_map=pd.read_csv(map_path) if os.path.exists(map_path) else pd.DataFrame()

# extract per store
summary={}
for name,code in stores.items():
    data={}
    # biz
    if biz_df is not None and not biz_df.empty:
        code_col=biz_df.columns[0]
        row=biz_df[biz_df[code_col].astype(str)==code]
        data['biz']=row.iloc[0] if not row.empty else None
    else:
        data['biz']=None
    # platform
    plat=None
    if platform_df is not None:
        code_col=None
        for c in platform_df.columns:
            if '代码' in str(c) or '��' in str(c) or '代' in str(c):
                code_col=c; break
        if code_col:
            row=platform_df[platform_df[code_col].astype(str)==code]
            plat=row.iloc[0] if not row.empty else None
    data['platform']=plat
    # lead
    lrow=None
    if lead_df is not None:
        # find column that contains code
        mask=None
        for c in lead_df.columns:
            if lead_df[c].astype(str).str.contains(code, na=False).any():
                mask=lead_df[c].astype(str).str.contains(code, na=False)
                break
        if mask is not None:
            rows=lead_df[mask]
            lrow=rows
    data['lead']=lrow
    # CSI stat
    crow=None
    if csi_stat is not None:
        mask=None
        for c in csi_stat.columns:
            if csi_stat[c].astype(str).str.contains(code, na=False).any():
                mask=csi_stat[c].astype(str).str.contains(code, na=False)
                break
        if mask is not None:
            crow=csi_stat[mask]
    data['csi_stat']=crow
    # CSI bad
    bad=None
    if csi_bad is not None:
        mask=None
        for c in csi_bad.columns:
            if csi_bad[c].astype(str).str.contains(code, na=False).any():
                mask=csi_bad[c].astype(str).str.contains(code, na=False)
                break
        if mask is not None:
            bad=csi_bad[mask]
    data['csi_bad']=bad
    summary[name]=data

# build markdown
report_date='2026-03-10'
md=[]
md.append(f"# KPI 每日全维度分析报告\n\n**报告日期**: {report_date}  \n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n")
md.append('| 店铺 | 代码 |'); md.append('|---|---|')
for k,v in stores.items():
    md.append(f"| {k} | {v} |")
md.append('\n---\n')

for store in stores:
    md.append(f"## {store}\n")
    s=summary[store]
    # 经营
    md.append('### 经营（日常）')
    if s['biz'] is not None:
        r=s['biz']
        def g(key_substrs):
            for c in r.index:
                for ks in key_substrs:
                    if ks in str(c):
                        return r[c]
            return None
        metrics={
            '服务总收入': g(['服务总收入','服务收入']),
            '零件总收入': g(['零件总收入','零件收入']),
            '工时总收入': g(['工时总收入','工时收入']),
            '普通维修产值': g(['普通维修产值']),
            '事故维修产值': g(['事故维修产值']),
            '进店台次': g(['进店', '台次']),
            '成交台次': g(['成交台次','成交批次']),
            '零件达成率': g(['零件达成']),
            '台次达成率': g(['台次达成']),
            '机油单车': g(['机油单车','机油']),
            '事故单车': g(['事故单车','事故单车']),
            'Q1累计零件': g(['Q1']),
        }
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
        for c in p.index[:10]:
            md.append(f"| {c} | {p[c]} |")
    else:
        md.append('（无平台数据）')
    # 客诉/线索
    md.append('\n### 客诉/线索')
    if s['lead'] is not None and not s['lead'].empty:
        df=s['lead']
        # compute counts
        total=len(df)
        # 未关闭
        unclosed=0; timeout=0; closed=0
        for col in df.columns:
            if '关闭' in str(col) or '状态' in str(col):
                status_col=col; break
        else:
            status_col=None
        if status_col:
            unclosed = df[df[status_col].astype(str).str.contains('未|未关|open', case=False, na=False)].shape[0]
            closed = df[df[status_col].astype(str).str.contains('已|关闭|close', case=False, na=False)].shape[0]
        # 超时时长
        for col in df.columns:
            if '超时' in str(col) or '处理' in str(col):
                try:
                    timeout = (df[col].fillna(0).astype(float) > 0).sum()
                    break
                except Exception:
                    continue
        md.append(f"- 客诉/线索总数: {total}\n- 未关闭: {unclosed}\n- 已关闭: {closed}\n- 超时时长>0: {timeout}")
        md.append('\n| 字段 | 示例值 |'); md.append('|---|---|')
        md.append(f"| 状态列样例 | {df.iloc[0][status_col] if status_col else ''} |")
    else:
        md.append('（无客诉/线索数据）')
    # CSI
    md.append('\n### CSI 自主调研')
    if s['csi_stat'] is not None and not s['csi_stat'].empty:
        cs=s['csi_stat']
        # pick first row
        r=cs.iloc[0]
        md.append('| 指标 | 数值 |'); md.append('|---|---|')
        for k in r.index:
            if any(x in str(k) for x in ['维修','评价','参与','满意']):
                md.append(f"| {k} | {r[k]} |")
    else:
        md.append('（无 CSI 统计数据）')
    md.append('\n#### 不满意客户')
    if s['csi_bad'] is not None and not s['csi_bad'].empty:
        bad=s['csi_bad']
        md.append(f"- 不满意客户数: {len(bad)}")
        cols=list(bad.columns[:6])
        md.append('| 字段 | 示例 |'); md.append('|---|---|')
        for c in cols:
            md.append(f"| {c} | {bad.iloc[0][c]} |")
    else:
        md.append('（无不满意客户）')
    md.append('\n---\n')

md_text='\n'.join(md)
md_path=os.path.join(workspace,'KPI 日报_20260310_full.md')
with open(md_path,'w',encoding='utf-8') as f:
    f.write(md_text)
print('MD updated', md_path)

# simple HTML with <pre> (for now; charts can be added but time)
html_path=os.path.join(workspace,'KPI 日报_20260310_full.html')
html=f"<html><head><meta charset='utf-8'><title>KPI 全维度报告</title></head><body><pre>{md_text}</pre></body></html>"
with open(html_path,'w',encoding='utf-8') as f:
    f.write(html)
print('HTML updated', html_path)
