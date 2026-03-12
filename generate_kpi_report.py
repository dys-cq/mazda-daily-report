"""
KPI 每日全维度分析报告生成脚本
从 E:/2026 年 KPI/每日分析/ 目录读取数据，模糊匹配文件名
"""
import os, pandas as pd, json, shutil, html, glob, re
from datetime import datetime

stores = ['重庆金团','重庆瀚达','重庆银马','重庆万事新','西藏鼎恒']
store_codes = {'重庆金团':'M18003','重庆瀚达':'M23002','重庆银马':'A28856','重庆万事新':'M18571','西藏鼎恒':'M18912'}

# ===== 路径设置 =====
daily_dir = 'E:/2026 年 KPI/每日分析'
if not os.path.exists(daily_dir):
    raise SystemExit(f'未找到目录：{daily_dir}')

# 自动创建今日任务文件夹
today = datetime.now().strftime('%Y-%m-%d')
run_folder = os.path.join(daily_dir, f'{today}-统计')
os.makedirs(run_folder, exist_ok=True)
print(f'Run folder: {run_folder}')

# ===== 模糊匹配文件 =====
def find_file(keywords):
    """在 daily_dir 中递归模糊匹配文件名，返回第一个匹配的文件"""
    try:
        for root, dirs, files in os.walk(daily_dir):
            for f in files:
                if f.startswith('~$'):
                    continue
                for kw in keywords:
                    if kw in f:
                        full = os.path.join(root, f)
                        print(f'Found: {f} (matched "{kw}")')
                        return full
    except Exception as e:
        print(f'Error scanning: {e}')
    return None

# 查找各类数据文件
aftermarket_file = find_file(['售后日报'])
csi_file = find_file(['CSI', '自主调研'])
platform_file = find_file(['保险平台'])
lead_file = find_file(['客诉', '线索工单'])

print(f'\nData files:')
print(f'  Aftermarket: {os.path.basename(aftermarket_file) if aftermarket_file else "NOT FOUND"}')
print(f'  CSI: {os.path.basename(csi_file) if csi_file else "NOT FOUND"}')
print(f'  Platform: {os.path.basename(platform_file) if platform_file else "NOT FOUND"}')
print(f'  Lead: {os.path.basename(lead_file) if lead_file else "NOT FOUND"}')

# ===== 辅助函数 =====
def fmt_pct(val):
    if val is None or str(val)=='nan' or val=='':
        return '0.00%'
    try:
        f=float(val)
        if 0 <= f <= 1:
            return f"{f*100:.2f}%"
        return f"{f:.2f}%"
    except:
        return str(val)

# ===== 读取经营数据 =====
biz_metrics = {}
if aftermarket_file:
    try:
        xl = pd.ExcelFile(aftermarket_file)
        # 查找包含 mazda 或 3 月的 sheet
        target_sheet = None
        for sn in xl.sheet_names:
            if 'mazda' in sn.lower() or ('3' in sn and '月' in sn):
                target_sheet = sn
                break
        
        if target_sheet:
            print(f'\nReading biz data from sheet: {target_sheet}')
            biz_df = pd.read_excel(aftermarket_file, sheet_name=target_sheet)
            print(f'  Shape: {biz_df.shape}')
            
            for st in stores:
                code = store_codes[st]
                row = biz_df[biz_df.iloc[:,0].astype(str)==code]
                if not row.empty:
                    r = row.iloc[0]
                    biz_metrics[st] = {
                        '服务总收入': int(r.iloc[4]) if len(r)>4 and pd.notna(r.iloc[4]) else 0,
                        '零件总收入': int(r.iloc[5]) if len(r)>5 and pd.notna(r.iloc[5]) else 0,
                        '工时总收入': int(r.iloc[6]) if len(r)>6 and pd.notna(r.iloc[6]) else 0,
                        '进店台次': int(r.iloc[7]) if len(r)>7 and pd.notna(r.iloc[7]) else 0,
                        '台次达成率': fmt_pct(r.iloc[8]) if len(r)>8 and pd.notna(r.iloc[8]) else '0.00%',
                    }
    except Exception as e:
        print(f'Error reading aftermarket: {e}')

# ===== 读取零附件数据 =====
parts_data = {}
if aftermarket_file:
    try:
        # 查找零附件 sheet
        for sn in xl.sheet_names:
            if '零附件' in sn or '附件' in sn:
                parts_df = pd.read_excel(aftermarket_file, sheet_name=sn)
                print(f'\nReading parts data from sheet: {sn}, shape: {parts_df.shape}')
                
                for st in stores:
                    code = store_codes[st]
                    row = parts_df[parts_df.iloc[:,0].astype(str)==code]
                    if not row.empty:
                        r = row.iloc[0]
                        parts_data[st] = {
                            '当月零附件目标': int(r.iloc[9]) if len(r)>9 and pd.notna(r.iloc[9]) else 0,
                            '当月零附件达成': int(r.iloc[10]) if len(r)>10 and pd.notna(r.iloc[10]) else 0,
                            '当月达成率': fmt_pct(r.iloc[11]) if len(r)>11 and pd.notna(r.iloc[11]) else '0.00%',
                            '当季度零附件目标': int(r.iloc[12]) if len(r)>12 and pd.notna(r.iloc[12]) else 0,
                            '当季度零附件达成': int(r.iloc[13]) if len(r)>13 and pd.notna(r.iloc[13]) else 0,
                            '当季度达成率': fmt_pct(r.iloc[14]) if len(r)>14 and pd.notna(r.iloc[14]) else '0.00%',
                        }
                break
    except Exception as e:
        print(f'Error reading parts: {e}')

# ===== 读取保险/平台数据 =====
platform_data = {}
if platform_file:
    try:
        print(f'\nReading platform data from: {platform_file}')
        xl_pf = pd.ExcelFile(platform_file)
        
        # 解析所有月份 sheet
        months_data = {}
        for sn in xl_pf.sheet_names:
            if sn.startswith(('1','2','3','4','5','6','7','8','9','10','11','12')) or '月' in sn:
                df = pd.read_excel(platform_file, sheet_name=sn)
                if df.shape[1] >= 8:
                    months_data[sn] = df
                    print(f'  Sheet {sn}: {df.shape}')
        
        # 按门店统计
        for st in stores:
            code = store_codes[st]
            pm = {}
            quarter_renew_sum = 0
            last_month_loyal = None
            
            for sn, df in months_data.items():
                # 按代码查找
                row = df[df.iloc[:,0].astype(str)==code]
                if row.empty:
                    # 按名称查找
                    row = df[df.iloc[:,1].astype(str).str.contains(st, na=False)]
                if row.empty:
                    continue
                
                r = row.iloc[0]
                # 列结构：[0 序号，1 经销商代码，2 经销商名称，3 区域，4 经理，5 新保出单，6 续保出单，7 续保录单，8 续保汇总，9 忠诚用户，10 续保率]
                col_map = {'新保出单':5, '续保出单':6, '续保录单':7, '续保汇总':8, '忠诚用户':9, '续保率':10}
                
                for label, col_idx in col_map.items():
                    if len(df.columns) > col_idx:
                        val = r.iloc[col_idx]
                        if label == '续保率':
                            pm[f'{sn}-{label}'] = fmt_pct(val)
                        else:
                            pm[f'{sn}-{label}'] = int(val) if pd.notna(val) else 0
                        
                        if label == '续保汇总':
                            try:
                                quarter_renew_sum += int(val) if pd.notna(val) else 0
                            except:
                                pass
                        
                        if label == '忠诚用户':
                            last_month_loyal = int(val) if pd.notna(val) else None
            
            pm['当季度续保汇总累加'] = quarter_renew_sum
            if last_month_loyal and last_month_loyal > 0:
                ref_rate = quarter_renew_sum / last_month_loyal
                pm['参考续保率'] = f"{ref_rate*100:.2f}%" if ref_rate <= 1 else f"{ref_rate:.2f}%"
            else:
                pm['参考续保率'] = '-'
            
            platform_data[st] = pm
    except Exception as e:
        print(f'Error reading platform: {e}')

# ===== 读取 CSI 数据 =====
csi_stats = {}
bad_lists = {}
if csi_file:
    try:
        print(f'\nReading CSI data from: {csi_file}')
        xl_csi = pd.ExcelFile(csi_file)
        csi_stat = pd.read_excel(csi_file, sheet_name=0)
        csi_bad = pd.read_excel(csi_file, sheet_name=xl_csi.sheet_names[-1])
        
        # 解析表头时间范围
        csi_header_map = {}
        for col in csi_stat.columns:
            if isinstance(col, str) and ':' in col:
                m = re.match(r'^(.*?)[：:]\s*(.*)$', col)
                if m:
                    csi_header_map[m.group(1).strip()] = m.group(2).strip()
        
        # 按门店统计
        for st in stores:
            row = csi_stat[csi_stat.iloc[:,0].astype(str).str.contains(st, na=False)]
            if not row.empty:
                r = row.iloc[0]
                csi_stats[st] = {
                    '经销商名称': st,
                    '本月维修合同数_label': '本月维修合同数',
                    '本月维修合同数': int(r.iloc[1]) if len(r)>1 and pd.notna(r.iloc[1]) else 0,
                    '评价工单结算范围': csi_header_map.get('评价工单结算范围', ''),
                    '直评日期范围': csi_header_map.get('直评日期范围', ''),
                    '评价客户数': int(r.iloc[2]) if len(r)>2 and pd.notna(r.iloc[2]) else 0,
                    '参与率': fmt_pct(r.iloc[3]) if len(r)>3 and pd.notna(r.iloc[3]) else '0.00%',
                    '满意客户数': int(r.iloc[4]) if len(r)>4 and pd.notna(r.iloc[4]) else 0,
                    '满意率': fmt_pct(r.iloc[5]) if len(r)>5 and pd.notna(r.iloc[5]) else '0.00%',
                }
        
        # 不满意客户
        if not csi_bad.empty:
            for st in stores:
                bad_rows = csi_bad[csi_bad.iloc[:,0].astype(str).str.contains(st, na=False)]
                if not bad_rows.empty:
                    bad_lists[st] = bad_rows.to_dict('records')
    except Exception as e:
        print(f'Error reading CSI: {e}')

# ===== 读取客诉/线索数据 =====
lead_stats = {}
if lead_file:
    try:
        print(f'\nReading lead data from: {lead_file}')
        if lead_file.endswith('.xls') or lead_file.endswith('.xlsx'):
            tables = [pd.read_excel(lead_file, sheet_name=sn) for sn in pd.ExcelFile(lead_file).sheet_names]
        else:
            tables = pd.read_html(lead_file, encoding='utf-8')
        
        lead_df = max(tables, key=lambda t: t.shape[0]) if tables else None
        if lead_df is not None:
            lead_df.columns = lead_df.iloc[0]
            lead_df = lead_df.iloc[1:]
            
            for st in stores:
                sub = lead_df[lead_df.iloc[:,0].astype(str).str.contains(st, na=False)]
                total = len(sub)
                lead_stats[st] = {'total': total, 'closed': 0, 'unclosed': total, 'timeout': 0}
    except Exception as e:
        print(f'Error reading leads: {e}')

# ===== 生成 Markdown =====
now = datetime.now().strftime('%Y-%m-%d %H:%M')
report_date = datetime.now().strftime('%Y-%m-%d')

md = ['# KPI 每日全维度分析报告', '', f'**报告日期**: {report_date}  ', f'**生成时间**: {now}  ', '']
for st in stores:
    md.append(f'## {st}')
    bm = biz_metrics.get(st, {})
    pm = platform_data.get(st, {})
    pd_d = parts_data.get(st, {})
    cs = csi_stats.get(st, {})
    
    for k, v in {**bm, **pd_d}.items():
        md.append(f"- {k}: {v}")
    
    if pm:
        md.append('\n### 保险/平台线索')
        for k, v in pm.items():
            md.append(f"- {k}: {v}")
    
    if cs:
        md.append('\n### CSI 自主调研')
        for k, v in cs.items():
            if k != '经销商名称':
                md.append(f"- {k}: {v}")
    
    md.append('')

md_text = '\n'.join(md)
md_out = os.path.join(run_folder, f'KPI 日报_{report_date.replace("-","")}_full.md')
with open(md_out, 'w', encoding='utf-8') as f:
    f.write(md_text)

# ===== 生成 HTML =====
cards = []
for st in stores:
    bm = biz_metrics.get(st, {})
    pm = platform_data.get(st, {})
    pd_d = parts_data.get(st, {})
    cs = csi_stats.get(st, {})
    ls = lead_stats.get(st, {'total':0, 'closed':0, 'unclosed':0, 'timeout':0})
    bad = bad_lists.get(st, [])
    
    all_biz = {**bm, **pd_d}
    biz_rows = ''.join([f"<tr><td>{html.escape(str(k))}</td><td>{html.escape(str(v) if v else '')}</td></tr>" for k,v in all_biz.items()]) or '<tr><td colspan="2">（无数据）</td></tr>'
    
    plat_rows = ''.join([f"<tr><td>{html.escape(str(k))}</td><td>{html.escape(str(v))}</td></tr>" for k,v in pm.items()]) if pm else '<tr><td colspan="2">（无平台数据）</td></tr>'
    
    csi_rows = ''.join([
        f"<tr><td>经销商名称</td><td>{html.escape(st)}</td></tr>",
        f"<tr><td>本月维修合同数</td><td>{html.escape(str(cs.get('本月维修合同数', 0)))}</td></tr>",
        f"<tr><td>评价工单结算范围</td><td>{html.escape(str(cs.get('评价工单结算范围', '')))}</td></tr>",
        f"<tr><td>直评日期范围</td><td>{html.escape(str(cs.get('直评日期范围', '')))}</td></tr>",
        f"<tr><td>评价客户数</td><td>{html.escape(str(cs.get('评价客户数', 0)))}</td></tr>",
        f"<tr><td>参与率</td><td>{html.escape(str(cs.get('参与率', '0.00%')))}</td></tr>",
        f"<tr><td>满意客户数</td><td>{html.escape(str(cs.get('满意客户数', 0)))}</td></tr>",
        f"<tr><td>满意率</td><td>{html.escape(str(cs.get('满意率', '0.00%')))}</td></tr>",
    ]) if cs else '<tr><td colspan="2">（无 CSI 数据）</td></tr>'
    
    if bad:
        bad_rows = ''.join([f"<tr><td>{html.escape(b.get('客诉所属经销商',''))}</td><td>{html.escape(str(b.get('直评时间','')))}</td><td>{html.escape(str(b.get('维修合同号','')))}</td><td>{html.escape(str(b.get('不满意点概述','')))}</td></tr>" for b in bad])
        bad_tbl = f"<table><thead><tr><th>经销商</th><th>时间</th><th>合同号</th><th>概述</th></tr></thead><tbody>{bad_rows}</tbody></table>"
    else:
        bad_tbl = '（本店无不满意客户）'
    
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
            <li>总数：<b>{ls.get('total',0)}</b></li>
            <li>未关闭：<b>{ls.get('unclosed',0)}</b></li>
            <li>已关闭：<b>{ls.get('closed',0)}</b></li>
            <li>超时：<b>{ls.get('timeout',0)}</b></li>
          </ul>
          <h3>CSI 自主调研</h3>
          <table><tbody>{csi_rows}</tbody></table>
          <h4>不满意客户</h4>
          {bad_tbl}
        </div>
      </div>
    </section>
    """)

# 图表数据
labels = stores
closed = [lead_stats.get(s,{}).get('closed',0) for s in stores]
unclosed = [lead_stats.get(s,{}).get('unclosed',0) for s in stores]
timeout = [lead_stats.get(s,{}).get('timeout',0) for s in stores]
part = [float(csi_stats.get(s,{}).get('参与率','0').strip('%')) if csi_stats.get(s) else 0 for s in stores]

html_text = f"""<!doctype html>
<html><head><meta charset='utf-8'><title>KPI 每日全维度分析报告</title>
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
<p>报告日期：{report_date} ｜ 生成时间：{now}</p>
<section class='card'><h3>总览图表</h3><canvas id='leadChart'></canvas><br/><canvas id='csiChart'></canvas></section>
{''.join(cards)}
</div>
<script>
new Chart(document.getElementById('leadChart'),{{type:'bar',data:{{labels:{json.dumps(labels)},datasets:[{{label:'已关闭',data:{json.dumps(closed)}}},{{label:'未关闭',data:{json.dumps(unclosed)}}},{{label:'超时>0',data:{json.dumps(timeout)}}}]}}}});
new Chart(document.getElementById('csiChart'),{{type:'line',data:{{labels:{json.dumps(labels)},datasets:[{{label:'CSI 参与率 (%)',data:{json.dumps(part)}}}]}}}});
</script></body></html>"""

html_out = os.path.join(run_folder, f'KPI 日报_{report_date.replace("-","")}_full.html')
with open(html_out, 'w', encoding='utf-8') as f:
    f.write(html_text)

# 同步到 workspace
ws = 'C:/Users/Administrator/.openclaw/workspace'
shutil.copyfile(md_out, os.path.join(ws, f'KPI 日报_{report_date.replace("-","")}_full.md'))
shutil.copyfile(html_out, os.path.join(ws, f'KPI 日报_{report_date.replace("-","")}_full.html'))

print(f'\nOK: {html_out}')
