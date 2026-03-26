import os
import re
from datetime import datetime
import pandas as pd

DAILY_DIR = r'E:\每日分析数据源'
WORKSPACE = r'C:\Users\Administrator\.openclaw\workspace'
TARGET_STORES = ['重庆金团', '重庆瀚达', '重庆银马', '重庆万事新', '西藏鼎恒']
STORE_CODES = {
    '重庆金团': 'M18003',
    '重庆瀚达': 'M23002',
    '重庆银马': 'A28856',
    '重庆万事新': 'M18571',
    '西藏鼎恒': 'M18912',
}


def latest_file(keyword):
    files = [f for f in os.listdir(DAILY_DIR) if keyword in f]
    if not files:
        return None
    files.sort(key=lambda x: os.path.getmtime(os.path.join(DAILY_DIR, x)), reverse=True)
    return os.path.join(DAILY_DIR, files[0])


def pct(v):
    if pd.isna(v):
        return '-'
    try:
        return f'{float(v) * 100:.2f}%'
    except Exception:
        return str(v)


def num(v, nd=2):
    if pd.isna(v):
        return '-'
    try:
        return f'{float(v):,.{nd}f}'
    except Exception:
        return str(v)


# 1) 经营数据
sh_file = latest_file('售后日报')
if not sh_file:
    raise SystemExit('未找到售后日报文件')
report_date_match = re.search(r'(20\d{6})', os.path.basename(sh_file))
report_date = datetime.strptime(report_date_match.group(1), '%Y%m%d').strftime('%Y-%m-%d') if report_date_match else datetime.now().strftime('%Y-%m-%d')

biz_df = pd.read_excel(sh_file, sheet_name='3月mazda')
parts_df = pd.read_excel(sh_file, sheet_name='零件-经销商明细')
taici_df = pd.read_excel(sh_file, sheet_name='台次日报跟踪表', header=1)

# 2) 平台数据
platform_file = latest_file('保险平台数据')
platform_sheets = pd.read_excel(platform_file, sheet_name=None) if platform_file else {}
platform_months = []
platform_current = None
for sname, df in platform_sheets.items():
    if '月' in sname or '日' in sname:
        if '经销商代码' in df.columns:
            platform_months.append((sname, df))
            if '3月' in sname:
                platform_current = df
if platform_current is None and platform_months:
    platform_current = platform_months[-1][1]

# 3) CSI
csi_file = latest_file('CSI')
csi_stat_raw = pd.read_excel(csi_file, sheet_name='统计表', header=1) if csi_file else pd.DataFrame()
csi_bad = pd.read_excel(csi_file, sheet_name='不满意客户清单') if csi_file else pd.DataFrame()

# 4) 客诉工单
lead_file = latest_file('客诉工单')
lead_df = pd.read_excel(lead_file) if lead_file else pd.DataFrame()

# 5) 预处理门店映射
parts_code_col = '经销商代码之计数'
biz_code_col = '经销商代码'
csi_code_col = '经销商代码'
lead_code_col = '经销商代码'

# 台次表按区域，不按经销商；用 3月mazda 中保养台次/事故车台次/零件明细中的机油单车事故单车即可

reports = []
html_sections = []

for store in TARGET_STORES:
    code = STORE_CODES[store]
    biz_row = biz_df[biz_df[biz_code_col].astype(str) == code]
    biz_row = biz_row.iloc[0] if not biz_row.empty else None

    parts_row = parts_df[parts_df[parts_code_col].astype(str) == code]
    parts_row = parts_row.iloc[0] if not parts_row.empty else None

    csi_row = csi_stat_raw[csi_stat_raw[csi_code_col].astype(str) == code]
    csi_row = csi_row.iloc[0] if not csi_row.empty else None

    bad_rows = csi_bad[csi_bad['经销商编码'].astype(str) == code] if not csi_bad.empty and '经销商编码' in csi_bad.columns else pd.DataFrame()

    leads = lead_df[lead_df[lead_code_col].astype(str) == code] if not lead_df.empty else pd.DataFrame()
    lead_total = len(leads)
    lead_unclosed = len(leads[~leads['业务状态'].astype(str).isin(['已关闭', '关闭'])]) if lead_total else 0
    lead_closed = len(leads[leads['业务状态'].astype(str).isin(['已关闭', '关闭'])]) if lead_total else 0
    timeout_count = int((pd.to_numeric(leads['超时时长（处理）'], errors='coerce').fillna(0) > 0).sum()) if lead_total and '超时时长（处理）' in leads.columns else 0

    plat_current = None
    quarter_sum = {'新保出单': 0, '续保出单': 0, '续保录单': 0, '续保汇总': 0}
    ref_rates = []
    for sname, df in platform_months:
        row = df[df['经销商代码'].astype(str) == code]
        if not row.empty:
            r = row.iloc[0]
            for k in quarter_sum:
                if k in r.index:
                    quarter_sum[k] += float(r[k]) if pd.notna(r[k]) else 0
            if '月续保率' in r.index and pd.notna(r['月续保率']):
                ref_rates.append(float(r['月续保率']))
            if platform_current is not None and sname == [x[0] for x in platform_months if x[1] is platform_current][0]:
                plat_current = r
    ref_rate = sum(ref_rates) / len(ref_rates) if ref_rates else None

    md = []
    md.append(f'## {store}')
    md.append('')
    md.append('### 经营数据')
    if biz_row is not None or parts_row is not None:
        md.append('| 指标 | 数值 |')
        md.append('|---|---|')
        if biz_row is not None:
            md.append(f"| 服务总收入 | {num(biz_row['服务总收入'])} |")
            md.append(f"| 零件总收入 | {num(biz_row['零件总收入'])} |")
            md.append(f"| 工时总收入 | {num(biz_row['工时总收入'])} |")
            md.append(f"| 进店台次(维修工单数) | {num(biz_row['维修工单数'], 0)} |")
            md.append(f"| 保养台次 | {num(biz_row['保养台次'], 0)} |")
            md.append(f"| 机油单车 | {num(parts_row['机油单车']) if parts_row is not None else '-'} |")
            md.append(f"| 事故单车 | {num(parts_row['事故单车']) if parts_row is not None else '-'} |")
        if parts_row is not None:
            md.append(f"| 当月零附件目标 | {num(parts_row['3月零附件目标'])} |")
            md.append(f"| 当月零附件达成 | {num(parts_row['3月零附件达成'])} |")
            md.append(f"| 当月零附件达成率 | {pct(parts_row['3月达成率'])} |")
            md.append(f"| Q1零件目标 | {num(parts_row['Q1零件目标'])} |")
            md.append(f"| Q1零件达成 | {num(parts_row['Q1零件达成'])} |")
            md.append(f"| Q1零件达成率 | {pct(parts_row['Q1达成率'])} |")
    else:
        md.append('（无经营数据）')

    md.append('')
    md.append('### 保险平台')
    if plat_current is not None:
        md.append('| 指标 | 数值 |')
        md.append('|---|---|')
        for k in ['新保出单', '续保出单', '续保录单', '续保汇总', '忠诚用户']:
            md.append(f'| {k} | {num(plat_current[k], 0)} |')
        md.append(f"| 当前续保率 | {pct(plat_current['月续保率'])} |")
        md.append(f"| 参考续保率（季度平均） | {pct(ref_rate) if ref_rate is not None else '-'} |")
        md.append(f"| 当季度续保汇总累加 | {num(quarter_sum['续保汇总'], 0)} |")
    else:
        md.append('（无保险平台数据）')

    md.append('')
    md.append('### 客诉/线索')
    md.append(f'- 总数：{lead_total}')
    md.append(f'- 未关闭：{lead_unclosed}')
    md.append(f'- 已关闭：{lead_closed}')
    md.append(f'- 超时>0：{timeout_count}')

    md.append('')
    md.append('### CSI')
    if csi_row is not None:
        md.append('| 指标 | 数值 |')
        md.append('|---|---|')
        md.append(f"| 本月维修合同数 | {num(csi_row['本月维修合同'], 0)} |")
        md.append(f"| 评价客户数 | {num(csi_row['评价客户数'], 0)} |")
        md.append(f"| 参与率 | {pct(csi_row['参与率'])} |")
        md.append(f"| 满意客户数 | {num(csi_row['满意客户数'], 0)} |")
        md.append(f"| 满意率 | {pct(csi_row['满意率'])} |")
    else:
        md.append('（无 CSI 统计数据）')

    md.append('')
    md.append('#### 不满意客户清单')
    if not bad_rows.empty:
        md.append('| 客诉所属经销商 | 直评时间 | 维修合同号 | 不满意点概述 |')
        md.append('|---|---|---|---|')
        for _, r in bad_rows.head(20).iterrows():
            bad_text = str(r.get('请问有哪些地方您觉得需要继续改善?（可多选）', ''))
            md.append(f"| {r.get('经销商','')} | {r.get('直评时间','')} | {r.get('维修合同号','')} | {bad_text} |")
    else:
        md.append('（本店无不满意客户）')

    reports.append('\n'.join(md))

    html_sections.append(f"<section><h2>{store}</h2><pre style='white-space:pre-wrap;font-family:Microsoft YaHei'>{'\n'.join(md[2:])}</pre></section>")

full_md = f"# KPI 每日全维度分析报告\n\n**报告日期**: {report_date}  \n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n" + '\n\n---\n\n'.join(reports) + '\n'

md_path = os.path.join(WORKSPACE, f'KPI 日报_{report_date.replace('-', '')}_full_fixed.md')
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(full_md)

html = f"<!doctype html><html><head><meta charset='utf-8'><title>KPI 每日全维度分析报告</title><style>body{{font-family:Microsoft YaHei,Arial,sans-serif;padding:24px;line-height:1.6}} table{{border-collapse:collapse;width:100%;margin:12px 0}} th,td{{border:1px solid #ddd;padding:8px}} th{{background:#f5f5f5}} section{{margin:24px 0;padding:16px;border:1px solid #eee;border-radius:8px}}</style></head><body><h1>KPI 每日全维度分析报告</h1><p>报告日期：{report_date}｜生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>{''.join(html_sections)}</body></html>"
html_path = os.path.join(WORKSPACE, f'KPI 日报_{report_date.replace('-', '')}_full_fixed.html')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(md_path)
print(html_path)
