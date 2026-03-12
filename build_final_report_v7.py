import os, pandas as pd, json, shutil, html
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

run_folder = os.path.join(daily, '2026-03-11-重新统计')
os.makedirs(run_folder, exist_ok=True)
files=os.listdir(daily)

lead_file=next((os.path.join(daily,f) for f in files if '线索' in f or '客诉' in f), None)
csi_file=next((os.path.join(daily,f) for f in files if f.lower().startswith('csi')), None)
# 保险/平台线索（跳过临时文件~$）
platform_file=next((os.path.join(daily,f) for f in files if ('平台' in f or 'ƽ' in f) and not f.startswith('~$')), None)

# lead
lead_df=None
if lead_file:
    try:
        tables=pd.read_html(lead_file, encoding='utf-8')
    except Exception:
        tables=pd.read_html(lead_file)
    lead_df=max(tables, key=lambda t:t.shape[1])
    lead_df.columns=lead_df.iloc[0]
    lead_df=lead_df.iloc[1:]

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

# 平台/保险
platform_df=None
platform_stats={}
if platform_file:
    try:
        platform_df=pd.read_excel(platform_file, sheet_name=0)
    except Exception:
        platform_df=None

if platform_df is not None and not platform_df.empty:
    # 按经销商名称匹配（列索引 2 通常是经销商名称）
    name_col_idx=2
    for st in stores:
        sub=platform_df[platform_df.iloc[:,name_col_idx].astype(str).str.contains(st, na=False)]
        if not sub.empty:
            r=sub.iloc[0]
            # 提取关键指标
            m={}
            for c in r.index[:12]:
                m[str(c)]=r[c]
            platform_stats[st]=m
        else:
            platform_stats[st]={}

# CSI
csi_stat=None
csi_bad=None
if csi_file:
    xl=pd.ExcelFile(csi_file)
    csi_stat=pd.read_excel(csi_file, sheet_name=0)
    csi_bad=pd.read_excel(csi_file, sheet_name=xl.sheet_names[-1])

# 解析 CSI 统计表头（含时间范围信息）
csi_header_map={}
if csi_stat is not None and not csi_stat.empty:
    for col in csi_stat.columns:
        if str(col).startswith('Unnamed'):
            continue
        m=pd.api.types.is_string_dtype(type(col)) or isinstance(col,str)
        if m:
            import re
            mm=re.match(r'^(.*?)[：:]\s*(.*)$', str(col))
            if mm:
                csi_header_map[mm.group(1).strip()]=mm.group(2).strip()

csi_stats={}
for st in stores:
    code=store_codes[st]
    data={'经销商名称':'','评价工单结算范围':'','本月维修合同数':0,'直评日期范围':'','评价客户数':0,'参与率':'0.00%','满意客户数':0,'满意率':'0.00%'}
    if csi_stat is not None and not csi_stat.empty:
        r=csi_stat[csi_stat.iloc[:,0].astype(str)==code]
        if not r.empty:
            row=r.iloc[0]
            data['经销商名称']=str(row.iloc[1])
            # 评价工单结算范围：从表头解析时间范围，而不是行内大区值
            data['评价工单结算范围']=csi_header_map.get('评价工单结算范围', str(row.iloc[2]))
            # 本月维修合同数：从行数据取值（列索引 4），带表头时间范围
            contract_cnt=float(row.iloc[4]) if pd.notna(row.iloc[4]) else 0
            contract_range=csi_header_map.get('本月维修合同', '')
            data['本月维修合同数']=int(contract_cnt)
            if contract_range:
                data['本月维修合同数_label']=f"本月维修合同数（{contract_range}）"
            else:
                data['本月维修合同数_label']='本月维修合同数'
            # 直评日期范围：从表头解析
            data['直评日期范围']=csi_header_map.get('直评日期', '')
            eval_cnt=float(row.iloc[5]) if pd.notna(row.iloc[5]) else 0
            part=float(row.iloc[6]) if pd.notna(row.iloc[6]) else 0
            sat_cnt=float(row.iloc[7]) if pd.notna(row.iloc[7]) else 0
            sat_rate=float(row.iloc[8]) if pd.notna(row.iloc[8]) else 0
            data['评价客户数']=int(eval_cnt)
            data['参与率']=f"{part*100:.2f}%" if part<=1 else f"{part:.2f}%"
            data['满意客户数']=int(sat_cnt)
            data['满意率']=f"{sat_rate*100:.2f}%" if sat_rate<=1 else f"{sat_rate:.2f}%"
    csi_stats[st]=data

bad_lists={}
if csi_bad is not None and not csi_bad.empty and csi_bad.shape[1] >= 4:
    for st in stores:
        code=store_codes[st]
        sub=csi_bad[csi_bad.iloc[:,3].astype(str)==code]
        rows=[]
        for _,r in sub.iterrows():
            rows.append({
                '客诉所属经销商': str(r.iloc[6]) if len(r)>6 else '',
                '直评时间': str(r.iloc[9]) if len(r)>9 else '',
                '维修合同号': str(r.iloc[0]) if len(r)>0 else '',
                '不满意点概述': str(r.iloc[13]) if len(r)>13 else '',
            })
        bad_lists[st]=rows

# biz minimal
biz_metrics={}
biz_csv='C:/Users/Administrator/.openclaw/workspace/sheet_3_3月mazda.csv'
if os.path.exists(biz_csv):
    biz_df=pd.read_csv(biz_csv)
    for st in stores:
        code=store_codes[st]
        row=biz_df[biz_df.iloc[:,0].astype(str)==code]
        m={}
        if not row.empty:
            r=row.iloc[0]
            cols=r.index
            def find_any(keys):
                for c in cols:
                    if any(k in str(c) for k in keys):
                        return r[c]
                return None
            # 辅助函数：百分比格式化
            def fmt_pct(val):
                if val is None or str(val)=='nan':
                    return None
                try:
                    f=float(val)
                    if 0 <= f <= 1:
                        return f"{f*100:.2f}%"
                    return f"{f:.2f}%"
                except Exception:
                    return str(val)

            m={
                '服务总收入': find_any(['服务总']),
                '零件总收入': find_any(['零件总']),
                '工时总收入': find_any(['工时总']),
                '进店台次': find_any(['进店','台']),
                '零件达成率': fmt_pct(find_any(['零件','达成'])),
                '台次达成率': fmt_pct(find_any(['台次','达成'])),
                '忠诚率': fmt_pct(find_any(['忠诚'])),
                '机油单车': find_any(['机油','单车']),
                '事故单车': find_any(['事故','单车']),
            }
        biz_metrics[st]=m

# markdown output (keep)
now=datetime.now().strftime('%Y-%m-%d %H:%M')
md=['# KPI 每日全维度分析报告', '', f'**报告日期**: 2026-03-10  ', f'**生成时间**: {now}  ', '']
for st in stores:
    md.append(f'## {st}')
    ls=lead_stats.get(st,{'total':0,'closed':0,'unclosed':0,'timeout':0})
    cs=csi_stats.get(st,{})
    md.append(f"- 客诉总数 {ls['total']} / 已关闭 {ls['closed']} / 未关闭 {ls['unclosed']} / 超时>0 {ls['timeout']}")
    md.append(f"- CSI 评价客户数 {cs.get('评价客户数',0)}，参与率 {cs.get('参与率','0.00%')}，满意率 {cs.get('满意率','0.00%')}")
    md.append('')
md_text='\n'.join(md)

md_out=os.path.join(run_folder,'KPI 日报_20260310_full.md')
with open(md_out,'w',encoding='utf-8') as f:
    f.write(md_text)

# HTML proper render
cards=[]
for st in stores:
    bm=biz_metrics.get(st,{})
    pm=platform_stats.get(st,{})
    ls=lead_stats.get(st,{'total':0,'closed':0,'unclosed':0,'timeout':0})
    cs=csi_stats.get(st,{})
    bad=bad_lists.get(st,[])

    biz_rows=''.join([f"<tr><td>{html.escape(str(k))}</td><td>{html.escape(str(v))}</td></tr>" for k,v in bm.items() if v is not None and str(v)!='nan']) or '<tr><td colspan="2">（无经营数据）</td></tr>'

    plat_rows=''.join([f"<tr><td>{html.escape(str(k))}</td><td>{html.escape(str(v))}</td></tr>" for k,v in pm.items() if v is not None and str(v)!='nan']) if pm else '<tr><td colspan="2">（无平台数据）</td></tr>'

    csi_rows=''.join([
        f"<tr><td>经销商名称</td><td>{html.escape(str(cs.get('经销商名称','')))}</td></tr>",
        f"<tr><td>{html.escape(cs.get('本月维修合同数_label','本月维修合同数'))}</td><td>{html.escape(str(cs.get('本月维修合同数',0)))}</td></tr>",
        f"<tr><td>评价工单结算范围</td><td>{html.escape(str(cs.get('评价工单结算范围','')))}</td></tr>",
        f"<tr><td>直评日期范围</td><td>{html.escape(str(cs.get('直评日期范围','')))}</td></tr>",
        f"<tr><td>评价客户数</td><td>{html.escape(str(cs.get('评价客户数',0)))}</td></tr>",
        f"<tr><td>参与率</td><td>{html.escape(str(cs.get('参与率','0.00%')))}</td></tr>",
        f"<tr><td>满意客户数</td><td>{html.escape(str(cs.get('满意客户数',0)))}</td></tr>",
        f"<tr><td>满意率</td><td>{html.escape(str(cs.get('满意率','0.00%')))}</td></tr>",
    ])

    if bad:
        bad_rows=''.join([f"<tr><td>{html.escape(b['客诉所属经销商'])}</td><td>{html.escape(b['直评时间'])}</td><td>{html.escape(b['维修合同号'])}</td><td>{html.escape(b['不满意点概述'])}</td></tr>" for b in bad])
        bad_tbl=f"<table><thead><tr><th>客诉所属经销商</th><th>直评时间</th><th>维修合同号</th><th>不满意点概述</th></tr></thead><tbody>{bad_rows}</tbody></table>"
    else:
        bad_tbl='（本店无不满意客户）'

    cards.append(f"""
    <section class='card'>
      <h2>{st}</h2>
      <div class='grid'>
        <div>
          <h3>经营（日常）</h3>
          <table><tbody>{biz_rows}</tbody></table>
          <h3>保险/平台线索</h3>
          <table><tbody>{plat_rows}</tbody></table>
        </div>
        <div>
          <h3>客诉/线索</h3>
          <ul>
            <li>客诉/线索总数：<b>{ls['total']}</b></li>
            <li>未关闭：<b>{ls['unclosed']}</b></li>
            <li>已关闭：<b>{ls['closed']}</b></li>
            <li>超时时长（处理）&gt;0：<b>{ls['timeout']}</b></li>
          </ul>
          <h3>CSI 自主调研</h3>
          <table><tbody>{csi_rows}</tbody></table>
          <h4>不满意客户</h4>
          {bad_tbl}
        </div>
      </div>
    </section>
    """)

labels=stores
closed=[lead_stats.get(s,{}).get('closed',0) for s in stores]
unclosed=[lead_stats.get(s,{}).get('unclosed',0) for s in stores]
timeout=[lead_stats.get(s,{}).get('timeout',0) for s in stores]
part=[float(csi_stats[s]['参与率'].strip('%')) if csi_stats.get(s) else 0 for s in stores]

html_text=f"""<!doctype html>
<html><head><meta charset='utf-8'><title>KPI重算版</title>
<script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
<style>
body{{font-family:'Microsoft YaHei',Arial;background:#f7f8fb;padding:20px;color:#222}}
.wrap{{max-width:1200px;margin:0 auto}}
.card{{background:#fff;border-radius:12px;padding:16px;margin:14px 0;box-shadow:0 2px 10px rgba(0,0,0,.08)}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
@media (max-width:900px){{.grid{{grid-template-columns:1fr}}}}
table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{border:1px solid #e5e7eb;padding:8px;vertical-align:top}}th{{background:#f3f4f6;text-align:left}}
canvas{{max-height:320px}}
</style></head><body><div class='wrap'>
<h1>KPI 每日全维度分析报告</h1>
<p>报告日期：2026-03-10 ｜ 生成时间：{now}</p>
<section class='card'><h3>总览图表</h3><canvas id='leadChart'></canvas><br/><canvas id='csiChart'></canvas></section>
{''.join(cards)}
</div>
<script>
new Chart(document.getElementById('leadChart'),{{type:'bar',data:{{labels:{json.dumps(labels)},datasets:[{{label:'已关闭',data:{json.dumps(closed)}}},{{label:'未关闭',data:{json.dumps(unclosed)}}},{{label:'超时>0',data:{json.dumps(timeout)}}}]}}}});
new Chart(document.getElementById('csiChart'),{{type:'line',data:{{labels:{json.dumps(labels)},datasets:[{{label:'CSI参与率(%)',data:{json.dumps(part)}}}]}}}});
</script></body></html>"""

html_out=os.path.join(run_folder,'KPI 日报_20260310_full.html')
with open(html_out,'w',encoding='utf-8') as f:
    f.write(html_text)

# sync to workspace canonical
ws='C:/Users/Administrator/.openclaw/workspace'
shutil.copyfile(md_out, os.path.join(ws,'KPI 日报_20260310_full.md'))
shutil.copyfile(html_out, os.path.join(ws,'KPI 日报_20260310_full.html'))
print('OK', html_out)
