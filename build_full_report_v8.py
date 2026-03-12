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

# 自动创建今日任务文件夹
today = datetime.now().strftime('%Y-%m-%d')
run_folder = os.path.join(daily, f'{today}-统计')
os.makedirs(run_folder, exist_ok=True)
print(f'Using run_folder: {run_folder}')

files=os.listdir(run_folder) if os.path.exists(run_folder) else []

# 查找各类数据文件
def find_file(patterns):
    for f in files:
        for p in patterns:
            if p in f:
                return os.path.join(run_folder, f)
    return None

# 辅助函数：百分比格式化
def fmt_pct(val):
    if val is None or str(val)=='nan' or val=='':
        return None
    try:
        f=float(val)
        if 0 <= f <= 1:
            return f"{f*100:.2f}%"
        return f"{f:.2f}%"
    except:
        return str(val)

# ===== 经营数据 (从 3 月 mazda sheet) =====
biz_metrics={}
biz_csv = find_file(['3 月 mazda', 'sheet_3_3'])
if biz_csv and os.path.exists(biz_csv):
    biz_df=pd.read_csv(biz_csv, encoding='utf-8-sig')
    print(f'Loaded biz: {biz_df.shape}')
    for st in stores:
        code=store_codes[st]
        row=biz_df[biz_df.iloc[:,0].astype(str)==code]
        m={}
        if not row.empty:
            r=row.iloc[0]
            # 列索引根据实际数据调整
            m={
                '服务总收入': int(r.iloc[4]) if pd.notna(r.iloc[4]) else 0,
                '零件总收入': int(r.iloc[5]) if pd.notna(r.iloc[5]) else 0,
                '工时总收入': int(r.iloc[6]) if pd.notna(r.iloc[6]) else 0,
                '进店台次': int(r.iloc[93]) if len(r)>93 and pd.notna(r.iloc[93]) else 0,
                '台次达成率': fmt_pct(r.iloc[158]) if len(r)>158 and pd.notna(r.iloc[158]) else '0.00%',
                '机油单车': int(float(r.iloc[20]) / max(1, float(r.iloc[93]))) if len(r)>93 and pd.notna(r.iloc[20]) and pd.notna(r.iloc[93]) else 0,
                '事故单车': int(float(r.iloc[11]) / max(1, float(r.iloc[79]))) if len(r)>79 and pd.notna(r.iloc[11]) and pd.notna(r.iloc[79]) else 0,
            }
        biz_metrics[st]=m

# ===== 零附件数据 =====
parts_data={}
parts_csv = find_file(['零附件', '附件明细'])
if parts_csv and os.path.exists(parts_csv):
    parts_df=pd.read_csv(parts_csv, encoding='utf-8-sig')
    print(f'Loaded parts: {parts_df.shape}')
    for st in stores:
        code=store_codes[st]
        row=parts_df[parts_df.iloc[:,0].astype(str)==code]
        if not row.empty:
            r=row.iloc[0]
            parts_data[st]={
                '当月零附件目标': int(r.iloc[9]) if len(r)>9 and pd.notna(r.iloc[9]) else 0,
                '当月零附件达成': int(r.iloc[10]) if len(r)>10 and pd.notna(r.iloc[10]) else 0,
                '当月达成率': fmt_pct(r.iloc[11]) if len(r)>11 and pd.notna(r.iloc[11]) else '0.00%',
                '当季度零附件目标': int(r.iloc[12]) if len(r)>12 and pd.notna(r.iloc[12]) else 0,
                '当季度零附件达成': int(r.iloc[13]) if len(r)>13 and pd.notna(r.iloc[13]) else 0,
                '当季度达成率': fmt_pct(r.iloc[14]) if len(r)>14 and pd.notna(r.iloc[14]) else '0.00%',
            }

# ===== 保险/平台数据 (从保险平台线索.xlsx) =====
platform_data={}
platform_file = find_file(['保险平台', '保险平台线索'])
if platform_file and os.path.exists(platform_file):
    print(f'Loading platform: {platform_file}')
    try:
        xl=pd.ExcelFile(platform_file)
        # 解析每个月的 sheet
        months_data = {}
        for sn in xl.sheet_names:
            # 匹配月份 sheet (1 月，2 月，3 月，etc.)
            if sn.startswith(('1','2','3','4','5','6','7','8','9','10','11','12')) or '月' in sn:
                df=pd.read_excel(platform_file, sheet_name=sn)
                if df.shape[1] >= 10:
                    months_data[sn] = df
                    print(f'  Sheet {sn}: {df.shape}')
        
        # 按门店统计
        for st in stores:
            code = store_codes[st]
            pm = {}
            quarter_renew_sum = 0
            last_month_loyal = None
            
            for sn, df in months_data.items():
                # 查找门店行
                row = df[df.iloc[:,0].astype(str)==code]
                if row.empty:
                    # 尝试按名称查找
                    row = df[df.iloc[:,1].astype(str).str.contains(st, na=False)]
                if row.empty:
                    continue
                
                r = row.iloc[0]
                # 列结构：[0 序号，1 经销商代码，2 经销商名称，3 区域，4 经理，5 新保出单，6 续保出单，7 续保录单，8 续保汇总，9 忠诚用户，10 续保率]
                col_map = {
                    '新保出单': 5, '续保出单': 6, '续保录单': 7, '续保汇总': 8, '忠诚用户': 9, '续保率': 10
                }
                
                for label, col_idx in col_map.items():
                    if len(df.columns) > col_idx:
                        val = r.iloc[col_idx]
                        if label == '续保率':
                            pm[f'{sn}-{label}'] = fmt_pct(val) if pd.notna(val) else '0.00%'
                        else:
                            pm[f'{sn}-{label}'] = int(val) if pd.notna(val) else 0
                        
                        # 累计季度续保汇总
                        if label == '续保汇总':
                            try:
                                quarter_renew_sum += int(val) if pd.notna(val) else 0
                            except:
                                pass
                        
                        # 最后一个月的忠诚用户
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
        print(f'Error loading platform: {e}')
else:
    print('No platform file found')

# ===== Markdown 输出 =====
now=datetime.now().strftime('%Y-%m-%d %H:%M')
md=['# KPI 每日全维度分析报告', '', f'**报告日期**: 2026-03-10  ', f'**生成时间**: {now}  ', '']
for st in stores:
    md.append(f'## {st}')
    bm=biz_metrics.get(st,{})
    pm=platform_data.get(st,{})
    pd_d=parts_data.get(st,{})
    for k,v in {**bm, **pd_d, **pm}.items():
        md.append(f"- {k}: {v}")
    md.append('')
md_text='\n'.join(md)

md_out=os.path.join(run_folder,'KPI 日报_20260310_full.md')
with open(md_out,'w',encoding='utf-8') as f:
    f.write(md_text)

# ===== HTML 输出 =====
cards=[]
for st in stores:
    bm=biz_metrics.get(st,{})
    pm=platform_data.get(st,{})
    pd_d=parts_data.get(st,{})
    
    all_biz = {**bm, **pd_d}
    biz_rows=''.join([f"<tr><td>{html.escape(str(k))}</td><td>{html.escape(str(v) if v else '')}</td></tr>" for k,v in all_biz.items() if v is not None]) or '<tr><td colspan="2">（无经营数据）</td></tr>'
    
    plat_rows=''.join([f"<tr><td>{html.escape(str(k))}</td><td>{html.escape(str(v))}</td></tr>" for k,v in pm.items()]) if pm else '<tr><td colspan="2">（无平台数据）</td></tr>'
    
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
          <ul><li>（暂无数据）</li></ul>
          <h3>CSI 自主调研</h3>
          <div>（暂无数据）</div>
          <h4>不满意客户</h4>
          （本店无不满意客户）
        </div>
      </div>
    </section>
    """)

html_text=f"""<!doctype html>
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
<p>报告日期：2026-03-10 ｜ 生成时间：{now}</p>
<section class='card'><h3>总览图表</h3><canvas id='leadChart'></canvas><br/><canvas id='csiChart'></canvas></section>
{''.join(cards)}
</div>
<script>
new Chart(document.getElementById('leadChart'),{{type:'bar',data:{{labels:[],datasets:[]}}}});
new Chart(document.getElementById('csiChart'),{{type:'line',data:{{labels:[],datasets:[]}}}});
</script></body></html>"""

html_out=os.path.join(run_folder,'KPI 日报_20260310_full.html')
with open(html_out,'w',encoding='utf-8') as f:
    f.write(html_text)

# sync to workspace
ws='C:/Users/Administrator/.openclaw/workspace'
shutil.copyfile(md_out, os.path.join(ws,'KPI 日报_20260310_full.md'))
shutil.copyfile(html_out, os.path.join(ws,'KPI 日报_20260310_full.html'))
print('OK', html_out)
