import os
import re
import json
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


def num_raw(v, default=0):
    if pd.isna(v):
        return default
    try:
        return float(v)
    except Exception:
        return default


def render_kv_table(title, rows):
    trs = ''.join([f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows])
    return f"<div class='panel'><h3>{title}</h3><table class='kv'>{trs}</table></div>"


sh_file = latest_file('售后日报')
report_date_match = re.search(r'(20\d{6})', os.path.basename(sh_file))
report_date = datetime.strptime(report_date_match.group(1), '%Y%m%d').strftime('%Y-%m-%d') if report_date_match else datetime.now().strftime('%Y-%m-%d')

biz_df = pd.read_excel(sh_file, sheet_name='3月mazda')
parts_df = pd.read_excel(sh_file, sheet_name='零件-经销商明细')

platform_file = latest_file('保险平台数据')
platform_sheets = pd.read_excel(platform_file, sheet_name=None) if platform_file else {}
platform_months = []
platform_current_name = None
for sname, df in platform_sheets.items():
    if ('月' in sname or '日' in sname) and '经销商代码' in df.columns:
        platform_months.append((sname, df))
        if '3月' in sname:
            platform_current_name = sname
if platform_current_name is None and platform_months:
    platform_current_name = platform_months[-1][0]

csi_file = latest_file('CSI')
csi_stat_raw = pd.read_excel(csi_file, sheet_name='统计表', header=1) if csi_file else pd.DataFrame()
csi_bad = pd.read_excel(csi_file, sheet_name='不满意客户清单') if csi_file else pd.DataFrame()
lead_file = latest_file('客诉工单')
lead_df = pd.read_excel(lead_file) if lead_file else pd.DataFrame()

parts_code_col = '经销商代码之计数'
biz_code_col = '经销商代码'

store_cards = []
chart_labels = []
service_income = []
lead_totals = []
csi_rates = []

for store in TARGET_STORES:
    code = STORE_CODES[store]
    biz_row = biz_df[biz_df[biz_code_col].astype(str) == code]
    biz_row = biz_row.iloc[0] if not biz_row.empty else None
    parts_row = parts_df[parts_df[parts_code_col].astype(str) == code]
    parts_row = parts_row.iloc[0] if not parts_row.empty else None
    csi_row = csi_stat_raw[csi_stat_raw['经销商代码'].astype(str) == code]
    csi_row = csi_row.iloc[0] if not csi_row.empty else None
    bad_rows = csi_bad[csi_bad['经销商编码'].astype(str) == code] if not csi_bad.empty and '经销商编码' in csi_bad.columns else pd.DataFrame()
    leads = lead_df[lead_df['经销商代码'].astype(str) == code] if not lead_df.empty else pd.DataFrame()

    lead_total = len(leads)
    lead_unclosed = len(leads[~leads['业务状态'].astype(str).isin(['已关闭', '关闭'])]) if lead_total else 0
    lead_closed = len(leads[leads['业务状态'].astype(str).isin(['已关闭', '关闭'])]) if lead_total else 0
    timeout_count = int((pd.to_numeric(leads['超时时长（处理）'], errors='coerce').fillna(0) > 0).sum()) if lead_total and '超时时长（处理）' in leads.columns else 0

    plat_current = None
    quarter_sum = {'续保汇总': 0}
    ref_rates = []
    for sname, df in platform_months:
        row = df[df['经销商代码'].astype(str) == code]
        if not row.empty:
            r = row.iloc[0]
            if '续保汇总' in r.index and pd.notna(r['续保汇总']):
                quarter_sum['续保汇总'] += float(r['续保汇总'])
            if '月续保率' in r.index and pd.notna(r['月续保率']):
                ref_rates.append(float(r['月续保率']))
            if sname == platform_current_name:
                plat_current = r
    ref_rate = sum(ref_rates) / len(ref_rates) if ref_rates else None

    biz_rows = []
    if biz_row is not None:
        biz_rows.extend([
            ('服务总收入', num(biz_row['服务总收入'])),
            ('零件总收入', num(biz_row['零件总收入'])),
            ('工时总收入', num(biz_row['工时总收入'])),
            ('进店台次(维修工单数)', num(biz_row['维修工单数'], 0)),
            ('保养台次', num(biz_row['保养台次'], 0)),
        ])
    if parts_row is not None:
        biz_rows.extend([
            ('机油单车', num(parts_row['机油单车'])),
            ('事故单车', num(parts_row['事故单车'])),
            ('当月零附件目标', num(parts_row['3月零附件目标'])),
            ('当月零附件达成', num(parts_row['3月零附件达成'])),
            ('当月零附件达成率', pct(parts_row['3月达成率'])),
            ('Q1零件目标', num(parts_row['Q1零件目标'])),
            ('Q1零件达成', num(parts_row['Q1零件达成'])),
            ('Q1零件达成率', pct(parts_row['Q1达成率'])),
        ])

    platform_rows = []
    if plat_current is not None:
        platform_rows.extend([
            ('新保出单', num(plat_current['新保出单'], 0)),
            ('续保出单', num(plat_current['续保出单'], 0)),
            ('续保录单', num(plat_current['续保录单'], 0)),
            ('续保汇总', num(plat_current['续保汇总'], 0)),
            ('忠诚用户', num(plat_current['忠诚用户'], 0)),
            ('当前续保率', pct(plat_current['月续保率'])),
            ('参考续保率（季度平均）', pct(ref_rate) if ref_rate is not None else '-'),
            ('当季度续保汇总累加', num(quarter_sum['续保汇总'], 0)),
        ])

    lead_rows = [
        ('总数', str(lead_total)),
        ('未关闭', str(lead_unclosed)),
        ('已关闭', str(lead_closed)),
        ('超时>0', str(timeout_count)),
    ]

    csi_rows = []
    if csi_row is not None:
        csi_rows.extend([
            ('本月维修合同数', num(csi_row['本月维修合同'], 0)),
            ('评价客户数', num(csi_row['评价客户数'], 0)),
            ('参与率', pct(csi_row['参与率'])),
            ('满意客户数', num(csi_row['满意客户数'], 0)),
            ('满意率', pct(csi_row['满意率'])),
        ])

    bad_html = "<div class='panel'><h3>不满意客户清单</h3><div class='empty'>（本店无不满意客户）</div></div>"
    if not bad_rows.empty:
        bad_trs = []
        for _, r in bad_rows.head(20).iterrows():
            bad_trs.append(
                f"<tr><td>{r.get('经销商','')}</td><td>{r.get('直评时间','')}</td><td>{r.get('维修合同号','')}</td><td>{r.get('请问有哪些地方您觉得需要继续改善?（可多选）','')}</td></tr>"
            )
        bad_html = (
            "<div class='panel wide'><h3>不满意客户清单</h3>"
            "<table><thead><tr><th>客诉所属经销商</th><th>直评时间</th><th>维修合同号</th><th>不满意点概述</th></tr></thead>"
            f"<tbody>{''.join(bad_trs)}</tbody></table></div>"
        )

    summary_cards = ''.join([
        f"<div class='mini-card'><div class='mini-label'>{label}</div><div class='mini-value'>{value}</div></div>"
        for label, value in [
            ('服务总收入', num(biz_row['服务总收入']) if biz_row is not None else '-'),
            ('客诉/线索总数', lead_total),
            ('CSI满意率', pct(csi_row['满意率']) if csi_row is not None else '-'),
            ('当前续保率', pct(plat_current['月续保率']) if plat_current is not None else '-'),
        ]
    ])

    sections = [
        render_kv_table('经营数据', biz_rows) if biz_rows else "<div class='panel'><h3>经营数据</h3><div class='empty'>（无经营数据）</div></div>",
        render_kv_table('保险平台', platform_rows) if platform_rows else "<div class='panel'><h3>保险平台</h3><div class='empty'>（无保险平台数据）</div></div>",
        render_kv_table('客诉 / 线索', lead_rows),
        render_kv_table('CSI', csi_rows) if csi_rows else "<div class='panel'><h3>CSI</h3><div class='empty'>（无 CSI 统计数据）</div></div>",
        bad_html,
    ]

    store_cards.append(f"""
    <section class='store-section'>
      <div class='store-header'>
        <div>
          <h2>{store}</h2>
          <div class='store-code'>经销商代码：{code}</div>
        </div>
      </div>
      <div class='mini-grid'>{summary_cards}</div>
      <div class='grid'>
        {''.join(sections)}
      </div>
    </section>
    """)

    chart_labels.append(store)
    service_income.append(num_raw(biz_row['服务总收入']) if biz_row is not None else 0)
    lead_totals.append(lead_total)
    csi_rates.append(round(num_raw(csi_row['满意率']) * 100, 2) if csi_row is not None else 0)

html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>KPI 每日全维度分析报告</title>
  <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
  <style>
    :root {{
      --bg: #f3f6fb;
      --card: #ffffff;
      --text: #1f2937;
      --muted: #6b7280;
      --line: #e5e7eb;
      --primary: #2563eb;
      --primary2: #0ea5e9;
      --green: #10b981;
      --orange: #f59e0b;
      --red: #ef4444;
      --shadow: 0 10px 30px rgba(15, 23, 42, .08);
      --radius: 16px;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: "Microsoft YaHei", Arial, sans-serif; color: var(--text); background: linear-gradient(180deg,#eef4ff 0,#f8fbff 120px,var(--bg) 120px); }}
    .wrap {{ max-width: 1440px; margin: 0 auto; padding: 28px; }}
    .hero {{ background: linear-gradient(135deg,#1d4ed8,#0ea5e9); color: #fff; border-radius: 24px; padding: 28px 32px; box-shadow: var(--shadow); }}
    .hero h1 {{ margin: 0 0 8px; font-size: 34px; }}
    .hero p {{ margin: 0; opacity: .92; }}
    .top-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 16px; margin: 20px 0 28px; }}
    .top-card, .panel, .chart-card, .store-section {{ background: var(--card); border-radius: var(--radius); box-shadow: var(--shadow); }}
    .top-card {{ padding: 18px 20px; }}
    .top-label {{ color: var(--muted); font-size: 13px; margin-bottom: 8px; }}
    .top-value {{ font-size: 28px; font-weight: 700; }}
    .chart-grid {{ display: grid; grid-template-columns: 2fr 1fr; gap: 18px; margin-bottom: 24px; }}
    .chart-card {{ padding: 18px; }}
    .chart-card h3 {{ margin: 0 0 12px; font-size: 18px; }}
    .store-section {{ padding: 20px; margin-bottom: 24px; }}
    .store-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }}
    .store-header h2 {{ margin: 0; font-size: 26px; }}
    .store-code {{ color: var(--muted); margin-top: 4px; }}
    .mini-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 12px; margin: 14px 0 18px; }}
    .mini-card {{ background: #f8fbff; border: 1px solid #e7eefc; border-radius: 14px; padding: 14px; }}
    .mini-label {{ color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .mini-value {{ font-weight: 700; font-size: 20px; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 16px; }}
    .panel {{ padding: 16px; border: 1px solid #eef2f7; }}
    .panel.wide {{ grid-column: 1 / -1; }}
    .panel h3 {{ margin: 0 0 12px; font-size: 18px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    .kv th, .kv td, table th, table td {{ border-bottom: 1px solid var(--line); padding: 10px 8px; text-align: left; vertical-align: top; }}
    .kv th {{ width: 42%; color: var(--muted); font-weight: 600; }}
    table thead th {{ color: var(--muted); font-weight: 700; background: #fafcff; }}
    .empty {{ color: var(--muted); padding: 8px 0; }}
    .footer {{ text-align: center; color: var(--muted); padding: 10px 0 24px; }}
    @media (max-width: 1100px) {{ .top-grid, .mini-grid, .grid, .chart-grid {{ grid-template-columns: 1fr 1fr; }} }}
    @media (max-width: 720px) {{ .top-grid, .mini-grid, .grid, .chart-grid {{ grid-template-columns: 1fr; }} .hero h1{{font-size:28px}} }}
  </style>
</head>
<body>
  <div class='wrap'>
    <section class='hero'>
      <h1>KPI 每日全维度分析报告</h1>
      <p>报告日期：{report_date} ｜ 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </section>

    <section class='top-grid'>
      <div class='top-card'><div class='top-label'>门店数量</div><div class='top-value'>{len(TARGET_STORES)}</div></div>
      <div class='top-card'><div class='top-label'>总服务收入</div><div class='top-value'>{num(sum(service_income), 2)}</div></div>
      <div class='top-card'><div class='top-label'>总客诉/线索</div><div class='top-value'>{sum(lead_totals)}</div></div>
      <div class='top-card'><div class='top-label'>CSI平均满意率</div><div class='top-value'>{(sum(csi_rates)/len(csi_rates)):.2f}%</div></div>
    </section>

    <section class='chart-grid'>
      <div class='chart-card'>
        <h3>各店服务总收入对比</h3>
        <canvas id='incomeChart' height='120'></canvas>
      </div>
      <div class='chart-card'>
        <h3>客诉 / 线索总数对比</h3>
        <canvas id='leadChart' height='120'></canvas>
      </div>
    </section>

    {''.join(store_cards)}

    <div class='footer'>本报告由系统自动生成</div>
  </div>

  <script>
    const labels = {json.dumps(chart_labels, ensure_ascii=False)};
    new Chart(document.getElementById('incomeChart'), {{
      type: 'bar',
      data: {{
        labels,
        datasets: [{{
          label: '服务总收入',
          data: {json.dumps(service_income)},
          backgroundColor: ['#2563eb','#0ea5e9','#10b981','#f59e0b','#8b5cf6'],
          borderRadius: 8
        }}]
      }},
      options: {{ plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true }} }} }}
    }});

    new Chart(document.getElementById('leadChart'), {{
      type: 'doughnut',
      data: {{
        labels,
        datasets: [{{
          data: {json.dumps(lead_totals)},
          backgroundColor: ['#2563eb','#0ea5e9','#10b981','#f59e0b','#ef4444']
        }}]
      }},
      options: {{ plugins: {{ legend: {{ position: 'bottom' }} }} }}
    }});
  </script>
</body>
</html>
"""

html_path = os.path.join(WORKSPACE, f'KPI 日报_{report_date.replace('-', '')}_full_fixed.html')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(html_path)
