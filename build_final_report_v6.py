import os, pandas as pd, json, shutil
from datetime import datetime

stores = ['重庆金团','重庆瀚达','重庆银马','重庆万事新','西藏鼎恒']
store_codes = {'重庆金团':'M18003','重庆瀚达':'M23002','重庆银马':'A28856','重庆万事新':'M18571','西藏鼎恒':'M18912'}

# locate daily path
base=None
for it in os.scandir('E:/'):
    if '2026' in it.name and 'KPI' in it.name and it.is_dir():
        base=it.path; break
if not base:
    raise SystemExit('未找到 2026 KPI 目录')
daily=None
for sub in os.scandir(base):
    if 'ÿ' in sub.name or '每' in sub.name:
        daily=sub.path; break
if not daily:
    raise SystemExit('未找到 每日分析 目录')

# create dated folder under daily
run_folder = os.path.join(daily, '2026-03-11-重新统计')
os.makedirs(run_folder, exist_ok=True)

# source files
files=os.listdir(daily)
lead_file=next((os.path.join(daily,f) for f in files if '线索' in f or '客诉' in f), None)
csi_file=next((os.path.join(daily,f) for f in files if f.lower().startswith('csi')), None)
platform_file=next((os.path.join(daily,f) for f in files if '平台' in f or 'ƽ̨' in f), None)

# load lead by utf-8
lead_df=None
if lead_file:
    tables=None
    try:
        tables=pd.read_html(lead_file, encoding='utf-8')
    except Exception:
        tables=pd.read_html(lead_file)
    lead_df=max(tables, key=lambda t:t.shape[1])
    lead_df.to_csv(os.path.join(run_folder,'lead_raw_utf8.csv'), index=False, encoding='utf-8-sig')
    lead_df.columns=lead_df.iloc[0]
    lead_df=lead_df.iloc[1:]
    lead_df.to_csv(os.path.join(run_folder,'lead_utf8_header.csv'), index=False, encoding='utf-8-sig')

# parse lead counts
lead_stats={}
if lead_df is not None:
    cols=list(lead_df.columns)
    name_col=cols[15] if len(cols)>15 else cols[-1]
    status_col=cols[8] if len(cols)>8 else cols[0]
    timeout_col=cols[-1]

    for st in stores:
        sub=lead_df[lead_df[name_col].astype(str).str.contains(st, na=False)]
        total=len(sub)
        closed=sub[sub[status_col].astype(str).str.contains('关闭|已|闭', na=False)].shape[0]
        unclosed=max(total-closed,0)
        timeout=(pd.to_numeric(sub[timeout_col].astype(str).str.extract(r'(\d+\.?\d*)', expand=False), errors='coerce').fillna(0)>0).sum()
        lead_stats[st]={'total':int(total),'closed':int(closed),'unclosed':int(unclosed),'timeout':int(timeout)}

# load csi
csi_stat=None
csi_bad=None
if csi_file:
    xl=pd.ExcelFile(csi_file)
    csi_stat=pd.read_excel(csi_file, sheet_name=0)
    csi_stat.to_csv(os.path.join(run_folder,'csi_stat.csv'), index=False, encoding='utf-8-sig')
    # last sheet is dissatisfied list in this file
    csi_bad=pd.read_excel(csi_file, sheet_name=xl.sheet_names[-1])
    csi_bad.to_csv(os.path.join(run_folder,'csi_bad.csv'), index=False, encoding='utf-8-sig')

# CSI format extraction by fixed positions from 统计表
csi_stats={}
for st in stores:
    code=store_codes[st]
    data={
        '经销商名称':'',
        '评价工单结算范围':'',
        '评价客户数':0,
        '参与率':'0.00%',
        '满意客户数':0,
        '满意率':'0.00%',
        '本月维修合同':0,
    }
    if csi_stat is not None and not csi_stat.empty:
        r=csi_stat[csi_stat.iloc[:,0].astype(str)==code]
        if not r.empty:
            row=r.iloc[0]
            # col positions inferred from source
            data['经销商名称']=str(row.iloc[1])
            data['评价工单结算范围']=str(row.iloc[2])
            data['本月维修合同']=int(row.iloc[4]) if pd.notna(row.iloc[4]) else 0
            eval_cnt=float(row.iloc[5]) if pd.notna(row.iloc[5]) else 0
            part=float(row.iloc[6]) if pd.notna(row.iloc[6]) else 0
            sat_cnt=float(row.iloc[7]) if pd.notna(row.iloc[7]) else 0
            sat_rate=float(row.iloc[8]) if pd.notna(row.iloc[8]) else 0
            data['评价客户数']=int(eval_cnt)
            data['参与率']=f"{part*100:.2f}%" if part<=1 else f"{part:.2f}%"
            data['满意客户数']=int(sat_cnt)
            data['满意率']=f"{sat_rate*100:.2f}%" if sat_rate<=1 else f"{sat_rate:.2f}%"
    csi_stats[st]=data

# dissatisfied extraction by code in column index 3
bad_lists={}
if csi_bad is not None and not csi_bad.empty and csi_bad.shape[1] >= 4:
    for st in stores:
        code=store_codes[st]
        sub=csi_bad[csi_bad.iloc[:,3].astype(str)==code]
        bad_rows=[]
        if not sub.empty:
            for _,r in sub.iterrows():
                bad_rows.append({
                    '客诉所属经销商': str(r.iloc[6]) if len(r)>6 else '',
                    '直评时间': str(r.iloc[9]) if len(r)>9 else '',
                    '维修合同号': str(r.iloc[0]) if len(r)>0 else '',
                    '不满意点概述': str(r.iloc[13]) if len(r)>13 else '',
                })
        bad_lists[st]=bad_rows

# business quick metrics from existing csv
biz_df=None
biz_csv='C:/Users/Administrator/.openclaw/workspace/sheet_3_3月mazda.csv'
if os.path.exists(biz_csv):
    biz_df=pd.read_csv(biz_csv)
biz_metrics={}
if biz_df is not None:
    for st in stores:
        code=store_codes[st]
        row=biz_df[biz_df.iloc[:,0].astype(str)==code]
        if row.empty:
            biz_metrics[st]={}
            continue
        r=row.iloc[0]
        cols=r.index
        def find_any(keys):
            for c in cols:
                if any(k in str(c) for k in keys):
                    return r[c]
            return None
        biz_metrics[st]={
            '服务总收入': find_any(['服务总']),
            '零件总收入': find_any(['零件总']),
            '工时总收入': find_any(['工时总']),
            '进店台次': find_any(['进店','台']),
            '零件达成率': find_any(['零件','达成']),
            '台次达成率': find_any(['台次','达成']),
            '机油单车': find_any(['机油','单车']),
            '事故单车': find_any(['事故','单车']),
        }

# markdown
now=datetime.now().strftime('%Y-%m-%d %H:%M')
md=[]
md.append(f"# KPI 每日全维度分析报告（重算版）\n\n**报告日期**: 2026-03-10  \n**生成时间**: {now}  \n**数据目录**: `{run_folder}`\n")
md.append('---')
for st in stores:
    md.append(f"\n## {st}\n")
    md.append('### 经营（日常）')
    bm=biz_metrics.get(st,{})
    if bm:
        md.append('| 指标 | 数值 |\n|---|---|')
        for k,v in bm.items():
            if v is not None and str(v)!='nan':
                md.append(f"| {k} | {v} |")
    else:
        md.append('（无经营数据）')

    md.append('\n### 客诉/线索')
    ls=lead_stats.get(st,{'total':0,'closed':0,'unclosed':0,'timeout':0})
    md.append(f"- 客诉/线索总数: {ls['total']}\n- 未关闭: {ls['unclosed']}\n- 已关闭: {ls['closed']}\n- 超时时长（处理）>0: {ls['timeout']}")

    md.append('\n### CSI 自主调研')
    cs=csi_stats.get(st)
    md.append('| 指标 | 数值 |\n|---|---|')
    md.append(f"| 经销商名称 | {cs['经销商名称']} |")
    md.append(f"| 评价工单结算范围 | {cs['评价工单结算范围']} |")
    md.append(f"| 评价客户数 | {cs['评价客户数']} |")
    md.append(f"| 参与率 | {cs['参与率']} |")
    md.append(f"| 满意客户数 | {cs['满意客户数']} |")
    md.append(f"| 满意率 | {cs['满意率']} |")

    md.append('\n#### 不满意客户')
    bad=bad_lists.get(st,[])
    if not bad:
        md.append('（本店无不满意客户）')
    else:
        md.append('| 客诉所属经销商 | 直评时间 | 维修合同号 | 不满意点概述 |\n|---|---|---|---|')
        for b in bad:
            md.append(f"| {b['客诉所属经销商']} | {b['直评时间']} | {b['维修合同号']} | {b['不满意点概述']} |")

    md.append('\n---')

md_text='\n'.join(md)
md_out=os.path.join(run_folder,'KPI 日报_20260310_full.md')
html_out=os.path.join(run_folder,'KPI 日报_20260310_full.html')
with open(md_out,'w',encoding='utf-8') as f:
    f.write(md_text)

# html interactive
labels=stores
closed=[lead_stats.get(s,{}).get('closed',0) for s in stores]
unclosed=[lead_stats.get(s,{}).get('unclosed',0) for s in stores]
timeout=[lead_stats.get(s,{}).get('timeout',0) for s in stores]
part=[float(csi_stats[s]['参与率'].strip('%')) for s in stores]

html=f"""<!doctype html><html><head><meta charset='utf-8'><title>KPI重算版</title>
<script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
<style>body{{font-family:微软雅黑,Arial;background:#f7f8fb;padding:20px}}.card{{background:#fff;border-radius:12px;padding:16px;margin:12px 0;box-shadow:0 2px 8px rgba(0,0,0,.08)}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ddd;padding:8px}}</style></head><body>
<h1>KPI 每日全维度分析报告（重算版）</h1><p>生成时间 {now}</p>
<div class='card'><canvas id='leadChart'></canvas></div>
<div class='card'><canvas id='csiChart'></canvas></div>
<div class='card'><pre>{md_text}</pre></div>
<script>
new Chart(document.getElementById('leadChart'),{{type:'bar',data:{{labels:{json.dumps(labels)},datasets:[{{label:'已关闭',data:{json.dumps(closed)}}},{{label:'未关闭',data:{json.dumps(unclosed)}}},{{label:'超时>0',data:{json.dumps(timeout)}}}]}}}});
new Chart(document.getElementById('csiChart'),{{type:'line',data:{{labels:{json.dumps(labels)},datasets:[{{label:'CSI参与率(%)',data:{json.dumps(part)}}}]}}}});
</script></body></html>"""
with open(html_out,'w',encoding='utf-8') as f:
    f.write(html)

# copy to workspace canonical paths
ws='C:/Users/Administrator/.openclaw/workspace'
shutil.copyfile(md_out, os.path.join(ws,'KPI 日报_20260310_full.md'))
shutil.copyfile(html_out, os.path.join(ws,'KPI 日报_20260310_full.html'))

print('DONE')
print(md_out)
print(html_out)
