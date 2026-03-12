import os, re, json, pandas as pd
from datetime import datetime

stores = {
    '重庆金团': '重庆金团',
    '重庆瀚达': '重庆瀚达',
    '重庆银马': '重庆银马',
    '重庆万事新': '重庆万事新',
    '西藏鼎恒': '西藏鼎恒',
}
workspace = os.path.expanduser('~/.openclaw/workspace')

# locate base/daily
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

# business
biz_path=os.path.join(workspace,'sheet_3_3月mazda.csv')
biz_df=pd.read_csv(biz_path) if os.path.exists(biz_path) else None

# platform
platform_df=None
for f in files:
    if '平台' in f or 'ƽ̨' in f:
        try:
            platform_df=pd.read_excel(os.path.join(daily,f), sheet_name=0)
        except Exception:
            platform_df=None
        break

# lead (UTF-8 read_html)
lead_df=None
for f in files:
    if '线索' in f or '客诉' in f:
        path=os.path.join(daily,f)
        try:
            tables=pd.read_html(path, encoding='utf-8')
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
        # pick sheet with 不满意
        bad_sheet=None
        for s in xl.sheet_names:
            if '不满' in s or '��' in s or '客' in s:
                bad_sheet=s; break
        if bad_sheet:
            try:
                csi_bad=pd.read_excel(path, sheet_name=bad_sheet)
            except Exception:
                csi_bad=None
        break

# helper pick column by keyword any

def pick_col(cols, kws):
    for c in cols:
        sc=str(c)
        if any(k in sc for k in kws):
            return c
    return None

summary={}
for store in stores:
    entry={}
    # biz by dealer short name column (col 1) matching store name
    if biz_df is not None:
        name_col=biz_df.columns[1]
        row=biz_df[biz_df[name_col].astype(str).str.contains(store, na=False)]
        entry['biz']=row.iloc[0] if not row.empty else None
    else:
        entry['biz']=None
    # platform by 经销商简称
    plat=None
    if platform_df is not None:
        name_col=pick_col(platform_df.columns, ['简称','经销商']) or platform_df.columns[2]
        row=platform_df[platform_df[name_col].astype(str).str.contains(store, na=False)]
        plat=row.iloc[0] if not row.empty else None
    entry['platform']=plat
    # lead by 经销商简称
    linfo=None
    if lead_df is not None:
        name_col=pick_col(lead_df.columns, ['经销商','简称']) or lead_df.columns[15] if len(lead_df.columns)>15 else lead_df.columns[-1]
        status_col=pick_col(lead_df.columns, ['状态','业务状态'])
        timeout_col=pick_col(lead_df.columns, ['超时','处理'])
        mask=lead_df[name_col].astype(str).str.contains(store, na=False)
        sub=lead_df[mask]
        if not sub.empty:
            total=len(sub)
            if status_col:
                unclosed=sub[sub[status_col].astype(str).str.contains('未', na=False)].shape[0]
                closed=sub[sub[status_col].astype(str).str.contains('已', na=False)].shape[0]
            else:
                unclosed=closed=0
            if timeout_col:
                timeout=(pd.to_numeric(sub[timeout_col].astype(str).str.extract(r'(\d+)', expand=False), errors='coerce').fillna(0) > 0).sum()
            else:
                timeout=0
            linfo={'total':total,'unclosed':unclosed,'closed':closed,'timeout':timeout,'sample':sub.head(1)}
    entry['lead']=linfo
    # csi stat
    cstat=None
    if csi_stat is not None:
        # 先用“经销商名称”定位行；若不存在再回退模糊匹配
        name_col=pick_col(csi_stat.columns, ['经销商名称']) or pick_col(csi_stat.columns, ['经销','4S','店']) or csi_stat.columns[1]
        rows=csi_stat[csi_stat[name_col].astype(str).str.contains(store, na=False)]
        if rows.empty:
            # 再尝试按经销商代码匹配
            code_col=pick_col(csi_stat.columns, ['经销商代码']) or csi_stat.columns[0]
            code_map={'重庆金团':'M18003','重庆瀚达':'M23002','重庆银马':'A28856','重庆万事新':'M18571','西藏鼎恒':'M18912'}
            code=code_map.get(store)
            if code:
                rows=csi_stat[csi_stat[code_col].astype(str).str.contains(code, na=False)]
        if not rows.empty:
            r=rows.iloc[0]
            # 列名中往往包含“字段：时间范围”，行0是中文字段名；这里统一映射到行0字段名
            header_map={}
            for col in csi_stat.columns:
                if str(col).startswith('Unnamed'):
                    continue
                m=re.match(r'^(.*?)[：:]\s*(.*)$', str(col))
                if m:
                    field=m.group(1).strip()
                    rng=m.group(2).strip()
                    header_map[field]=rng

            # 统计表第一行通常是“字段名行”（经销商代码/经销商名称/本月维修合同...）
            # 先把当前门店行映射成“字段名 -> 数值”，避免列标题与数据错位导致取值错误
            label_row=None
            code_col_guess=pick_col(csi_stat.columns, ['统计周期','经销商代码']) or csi_stat.columns[0]
            label_rows=csi_stat[csi_stat[code_col_guess].astype(str).str.contains('经销商代码', na=False)]
            if not label_rows.empty:
                label_row=label_rows.iloc[0]
            else:
                label_row=csi_stat.iloc[0]

            field_value={}
            for k in r.index:
                key=str(k)
                val=r[k]

                # 列标题（常含“字段:时间范围”）
                mkey=re.match(r'^(.*?)[：:]\s*(.*)$', key)
                key_base=(mkey.group(1).strip() if mkey else key)
                field_value[key_base]=val

                # 第一行字段名（如：经销商名称/本月维修合同/评价客户数...）
                fld=str(label_row.get(k, '')).strip()
                if fld and fld.lower() != 'nan':
                    field_value[fld]=val

            keep={}
            # 基础字段
            if '经销商名称' in field_value:
                keep['经销商名称']=field_value['经销商名称']

            # 本月维修合同数（新增）
            if '本月维修合同' in field_value:
                rng=header_map.get('本月维修合同')
                kname='本月维修合同数' + (f'（{rng}）' if rng else '')
                keep[kname]=field_value['本月维修合同']

            # 评价工单结算范围：必须展示时间范围，而非大区（如“西区”）
            if '评价工单结算范围' in header_map:
                keep['评价工单结算范围']=header_map['评价工单结算范围']
            elif '评价工单结算范围' in field_value:
                keep['评价工单结算范围']=field_value['评价工单结算范围']

            # 直评日期范围（来自统计表头）
            if '直评日期' in header_map:
                keep['直评日期范围']=header_map['直评日期']

            # 其余 CSI 指标
            for fld in ['评价客户数','参与率','满意客户数','满意率']:
                if fld in field_value:
                    keep[fld]=field_value[fld]

            # 若上面未提取到，按关键词兜底
            if not keep:
                for k in r.index:
                    if any(x in str(k) for x in ['维修','合同','评价','参与','满意','率']):
                        keep[k]=r[k]
            cstat=keep
    entry['csi_stat']=cstat
    # csi bad
    cbad=None
    if csi_bad is not None:
        name_col=pick_col(csi_bad.columns, ['经销','店','4S']) or csi_bad.columns[1]
        mask=csi_bad[name_col].astype(str).str.contains(store, na=False)
        rows=csi_bad[mask]
        if not rows.empty:
            cbad=rows
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
    # 经营
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
    # 平台
    md.append('\n### 保险/平台线索')
    if s['platform'] is not None:
        p=s['platform']; md.append('| 指标 | 数值 |'); md.append('|---|---|')
        for c in p.index[:12]:
            md.append(f"| {c} | {p[c]} |")
    else:
        md.append('（无平台数据）')
    # 客诉/线索
    md.append('\n### 客诉/线索')
    if s['lead'] is not None:
        info=s['lead']; md.append(f"- 总数: {info['total']}\n- 未关闭: {info['unclosed']}\n- 已关闭: {info['closed']}\n- 超时>0: {info['timeout']}")
        md.append('| 字段 | 示例 |'); md.append('|---|---|')
        for c in info['sample'].columns[:4]:
            md.append(f"| {c} | {info['sample'].iloc[0][c]} |")
    else:
        md.append('（无客诉/线索数据）')
    # CSI
    md.append('\n### CSI 自主调研')
    if s['csi_stat']:
        md.append('| 指标 | 数值 |'); md.append('|---|---|')
        if s['csi_stat']:
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
        md.append('（本店无不满意客户）')
    md.append('\n---\n')

md_text='\n'.join(md)
md_path=os.path.join(workspace,'KPI 日报_20260310_full.md')
with open(md_path,'w',encoding='utf-8') as f:
    f.write(md_text)
print('MD written', md_path)

def esc(x):
    s='' if x is None else str(x)
    return (s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;'))

def fmt_metric(name, val):
    # 比率字段转百分比显示
    if val is None or str(val)=='nan':
        return ''
    if any(k in str(name) for k in ['率']):
        try:
            f=float(val)
            if 0 <= f <= 1:
                return f"{f*100:.2f}%"
            return f"{f:.2f}%"
        except Exception:
            return esc(val)
    return esc(val)

html_parts=[]
html_parts.append("""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>KPI 每日全维度分析报告</title>
  <style>
    body{font-family:'Microsoft YaHei',Arial,sans-serif;background:#f6f8fb;color:#1f2937;margin:0;padding:20px}
    .container{max-width:1200px;margin:0 auto}
    .title{background:#fff;padding:20px 24px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,.06);margin-bottom:16px}
    .store{background:#fff;padding:18px 20px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,.06);margin-bottom:16px}
    h1{margin:0 0 8px;color:#0f5fd6}
    h2{margin:8px 0 12px;color:#0f5fd6}
    h3{margin:12px 0 8px;color:#374151}
    .meta{color:#6b7280;font-size:14px}
    table{width:100%;border-collapse:collapse;margin:8px 0 14px;background:#fff}
    th,td{border:1px solid #e5e7eb;padding:8px 10px;text-align:left;font-size:14px}
    th{background:#eff6ff}
    ul{margin:6px 0 12px 18px}
    li{margin:4px 0}
  </style>
</head>
<body><div class="container">
""")

html_parts.append(f"<div class='title'><h1>KPI 每日全维度分析报告</h1><div class='meta'>报告日期：{esc(report_date)} | 生成时间：{esc(datetime.now().strftime('%Y-%m-%d %H:%M'))}</div></div>")

for store in stores:
    s=summary[store]
    html_parts.append(f"<section class='store'><h2>{esc(store)}</h2>")

    # 经营
    html_parts.append("<h3>经营（日常）</h3>")
    if s['biz'] is not None:
        r=s['biz']; cols=r.index
        def anyv(keys):
            for c in cols:
                if any(k in str(c) for k in keys):
                    return r[c]
            return None
        metrics=[
            ('服务总收入', anyv(['服务总'])), ('零件总收入', anyv(['零件总'])), ('工时总收入', anyv(['工时总'])),
            ('普通维修产值', anyv(['普通维修产值'])), ('事故维修产值', anyv(['事故维修产值'])),
            ('进店台次', anyv(['进店','台次'])), ('成交台次', anyv(['成交台次','成交批次'])),
            ('零件达成率', anyv(['零件','达成'])), ('台次达成率', anyv(['台次','达成'])),
            ('机油单车', anyv(['机油','单车'])), ('事故单车', anyv(['事故','单车'])), ('Q1累计零件', anyv(['Q1']))
        ]
        html_parts.append("<table><tr><th>指标</th><th>数值</th></tr>")
        for k,v in metrics:
            if v is not None and str(v)!='nan':
                html_parts.append(f"<tr><td>{esc(k)}</td><td>{fmt_metric(k,v)}</td></tr>")
        html_parts.append("</table>")
    else:
        html_parts.append("<div>（无经营数据）</div>")

    # 平台
    html_parts.append("<h3>保险/平台线索</h3>")
    if s['platform'] is not None:
        p=s['platform']
        html_parts.append("<table><tr><th>指标</th><th>数值</th></tr>")
        for c in p.index[:12]:
            html_parts.append(f"<tr><td>{esc(c)}</td><td>{esc(p[c])}</td></tr>")
        html_parts.append("</table>")
    else:
        html_parts.append("<div>（无平台数据）</div>")

    # 客诉/线索
    html_parts.append("<h3>客诉/线索</h3>")
    if s['lead'] is not None:
        info=s['lead']
        html_parts.append(f"<ul><li>总数: {esc(info['total'])}</li><li>未关闭: {esc(info['unclosed'])}</li><li>已关闭: {esc(info['closed'])}</li><li>超时&gt;0: {esc(info['timeout'])}</li></ul>")
        html_parts.append("<table><tr><th>字段</th><th>示例</th></tr>")
        for c in info['sample'].columns[:4]:
            html_parts.append(f"<tr><td>{esc(c)}</td><td>{esc(info['sample'].iloc[0][c])}</td></tr>")
        html_parts.append("</table>")
    else:
        html_parts.append("<div>（无客诉/线索数据）</div>")

    # CSI
    html_parts.append("<h3>CSI 自主调研</h3>")
    if s['csi_stat']:
        html_parts.append("<table><tr><th>指标</th><th>数值</th></tr>")
        for k,v in s['csi_stat'].items():
            html_parts.append(f"<tr><td>{esc(k)}</td><td>{fmt_metric(k,v)}</td></tr>")
        html_parts.append("</table>")
    else:
        html_parts.append("<div>（无 CSI 统计数据）</div>")

    html_parts.append("<h3>不满意客户</h3>")
    if s['csi_bad'] is not None:
        bad=s['csi_bad']
        html_parts.append(f"<div>不满意客户数：{len(bad)}</div>")
        html_parts.append("<table><tr><th>字段</th><th>示例</th></tr>")
        for c in bad.columns[:6]:
            html_parts.append(f"<tr><td>{esc(c)}</td><td>{esc(bad.iloc[0][c])}</td></tr>")
        html_parts.append("</table>")
    else:
        html_parts.append("<div>（本店无不满意客户）</div>")

    html_parts.append("</section>")

html_parts.append("</div></body></html>")

html_path=os.path.join(workspace,'KPI 日报_20260310_full.html')
with open(html_path,'w',encoding='utf-8') as f:
    f.write(''.join(html_parts))
print('HTML written', html_path)
