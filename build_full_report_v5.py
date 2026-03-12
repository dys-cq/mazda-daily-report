import os, re, pandas as pd
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

            keep={}
            for k in r.index:
                key=str(k)
                val=r[k]
                # 把“字段：范围”拆开，避免把大区值（如西区）错当成结算范围展示
                mkey=re.match(r'^(.*?)[：:]\s*(.*)$', key)
                key_base=(mkey.group(1).strip() if mkey else key)
                key_range=(mkey.group(2).strip() if mkey else '')

                # 仅保留核心 CSI 指标字段
                if any(x in key_base for x in ['经销商名称','评价工单结算范围','本月维修合同','评价客户数','参与率','满意客户数','满意率']):
                    display_key=key_base
                    display_val=val

                    if key_base=='评价工单结算范围':
                        # 按需求：此项应展示“结算时间范围”，而不是行内的大区值（西区）
                        display_val=key_range or header_map.get('评价工单结算范围', val)

                    if key_base in ['本月维修合同','直评日期']:
                        rng=key_range or header_map.get(key_base)
                        if rng:
                            display_key=f"{key_base}（{rng}）"

                    keep[display_key]=display_val

            # 新增：直评日期范围（来自统计表头“直评日期：xxxx-xxxx”）
            if '直评日期' in header_map:
                keep['直评日期范围']=header_map['直评日期']

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

html_path=os.path.join(workspace,'KPI 日报_20260310_full.html')
html=f"<html><head><meta charset='utf-8'><title>KPI 全维度报告</title></head><body><pre>{md_text}</pre></body></html>"
with open(html_path,'w',encoding='utf-8') as f:
    f.write(html)
print('HTML written', html_path)
