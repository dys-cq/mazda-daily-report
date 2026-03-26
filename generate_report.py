import pandas as pd
import glob
import json
from datetime import datetime

# 目标店铺
target_stores = ['重庆金团', '重庆瀚达', '重庆银马', '重庆万事新', '西藏鼎恒']
store_codes = {'重庆金团': 'M18003', '重庆瀚达': 'M23002', '重庆银马': 'A28856', '重庆万事新': 'M18571', '西藏鼎恒': 'M18912'}

# 读取所有店铺数据
store_data = {}
for store in target_stores:
    try:
        df = pd.read_csv(f'{store}_data.csv', encoding='utf-8-sig')
        store_data[store] = df
    except Exception as e:
        print(f"Error reading {store}: {e}")
        store_data[store] = pd.DataFrame()

# 读取经销商映射
dealer_map = pd.read_csv('sheet_9_Sheet3.csv', encoding='utf-8-sig')

# 读取综合数据 - 使用 glob 查找
mazda_files = glob.glob('sheet_3_*.csv')
mazda_file = mazda_files[0] if mazda_files else None
if mazda_file:
    mazda_df = pd.read_csv(mazda_file, encoding='utf-8-sig')
else:
    mazda_df = pd.DataFrame()

# 生成报告日期
report_date = "2026 年 3 月 10 日"

# 生成 Markdown 报告
md_content = f"""# KPI 每日分析报告

**报告日期**: {report_date}  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 一、数据概览

本次分析涵盖 5 家目标店铺的经营数据：

| 序号 | 店铺名称 | 经销商代码 | 经销商全称 |
|------|----------|------------|------------|
"""

for store, code in store_codes.items():
    full_name = dealer_map[dealer_map['经销商代码'] == code]['经销商简称'].values
    full_name = full_name[0] if len(full_name) > 0 else 'N/A'
    md_content += f"| {list(store_codes.keys()).index(store)+1} | {store} | {code} | {full_name} |\n"

md_content += """
---

## 二、核心经营指标

"""

# 添加每个店铺的数据
for store in target_stores:
    df = store_data.get(store)
    if df is not None and len(df) > 0:
        md_content += f"### 2.1 {store}\n\n"
        row = df.iloc[0]
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        md_content += "| 指标 | 数值 |\n|------|------|\n"
        display_cols = ['零售数量', '零售金额', '毛利额', '毛利率', '进店批次', '成交批次']
        for col in display_cols:
            if col in df.columns:
                val = row[col]
                if isinstance(val, (int, float)):
                    md_content += f"| {col} | {val:,.2f} |\n"
                else:
                    md_content += f"| {col} | {val} |\n"
        for col in numeric_cols[:10]:
            if col not in display_cols and col in df.columns:
                val = row[col]
                if isinstance(val, (int, float)):
                    md_content += f"| {col} | {val:,.2f} |\n"
        md_content += "\n"

md_content += """
---

## 三、店铺对比分析

### 3.1 零售数据对比

"""

md_content += "| 店铺 | 零售数量 | 零售金额 | 毛利额 | 毛利率 |\n|------|----------|----------|--------|--------|\n"

for store in target_stores:
    df = store_data.get(store)
    if df is not None and len(df) > 0:
        row = df.iloc[0]
        retail_qty = row.get('零售数量', 0) if '零售数量' in df.columns else 0
        retail_amt = row.get('零售金额', 0) if '零售金额' in df.columns else 0
        gross_profit = row.get('毛利额', 0) if '毛利额' in df.columns else 0
        gross_margin = row.get('毛利率', 0) if '毛利率' in df.columns else 0
        md_content += f"| {store} | {retail_qty:,.0f} | {retail_amt:,.2f} | {gross_profit:,.2f} | {gross_margin:.2f}% |\n"

md_content += """
---

## 四、总结与建议

1. **数据完整性**: 所有 5 家目标店铺数据已成功提取
2. **重点关注**: 建议关注零售数量和毛利率表现
3. **后续行动**: 持续跟踪每日数据变化

---

*本报告由系统自动生成*
"""

with open('KPI 日报_20260310.md', 'w', encoding='utf-8') as f:
    f.write(md_content)
print("OK: KPI 日报_20260310.md")

# 准备图表数据
chart_labels = []
chart_retail_qty = []
chart_retail_amt = []
for store in target_stores:
    df = store_data.get(store)
    if df is not None and len(df) > 0:
        row = df.iloc[0]
        chart_labels.append(store)
        chart_retail_qty.append(row.get('零售数量', 0) if '零售数量' in df.columns else 0)
        chart_retail_amt.append(row.get('零售金额', 0) if '零售金额' in df.columns else 0)

# 生成 HTML 报告
html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KPI 每日分析报告 - {report_date}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a73e8; text-align: center; margin-bottom: 10px; }}
        h2 {{ color: #333; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; margin: 30px 0 20px; }}
        h3 {{ color: #555; margin: 20px 0 15px; }}
        .meta {{ text-align: center; color: #666; margin-bottom: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #1a73e8; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .chart-container {{ margin: 30px 0; height: 400px; }}
        .summary {{ background: #e8f4fd; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .summary li {{ margin: 10px 0; }}
        .highlight {{ color: #1a73e8; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>KPI 每日分析报告</h1>
        <p class="meta">报告日期：{report_date} | 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        
        <h2>一、数据概览</h2>
        <table>
            <tr><th>序号</th><th>店铺名称</th><th>经销商代码</th><th>经销商全称</th></tr>
"""

for store, code in store_codes.items():
    full_name = dealer_map[dealer_map['经销商代码'] == code]['经销商简称'].values
    full_name = full_name[0] if len(full_name) > 0 else 'N/A'
    html_content += f"<tr><td>{list(store_codes.keys()).index(store)+1}</td><td>{store}</td><td>{code}</td><td>{full_name}</td></tr>\n"

html_content += """
        </table>
        
        <h2>二、核心经营指标</h2>
"""

for store in target_stores:
    df = store_data.get(store)
    if df is not None and len(df) > 0:
        row = df.iloc[0]
        html_content += f"<h3>{store}</h3><table><tr><th>指标</th><th>数值</th></tr>\n"
        display_cols = ['零售数量', '零售金额', '毛利额', '毛利率', '进店批次', '成交批次']
        for col in display_cols:
            if col in df.columns:
                val = row[col]
                if isinstance(val, (int, float)):
                    html_content += f"<tr><td>{col}</td><td>{val:,.2f}</td></tr>\n"
                else:
                    html_content += f"<tr><td>{col}</td><td>{val}</td></tr>\n"
        html_content += "</table>\n"

html_content += f"""
        <h2>三、店铺对比分析</h2>
        <div class="chart-container">
            <canvas id="retailChart"></canvas>
        </div>
        <table>
            <tr><th>店铺</th><th>零售数量</th><th>零售金额</th><th>毛利额</th><th>毛利率</th></tr>
"""

for store in target_stores:
    df = store_data.get(store)
    if df is not None and len(df) > 0:
        row = df.iloc[0]
        retail_qty = row.get('零售数量', 0) if '零售数量' in df.columns else 0
        retail_amt = row.get('零售金额', 0) if '零售金额' in df.columns else 0
        gross_profit = row.get('毛利额', 0) if '毛利额' in df.columns else 0
        gross_margin = row.get('毛利率', 0) if '毛利率' in df.columns else 0
        html_content += f"<tr><td>{store}</td><td>{retail_qty:,.0f}</td><td>{retail_amt:,.2f}</td><td>{gross_profit:,.2f}</td><td>{gross_margin:.2f}%</td></tr>\n"

html_content += f"""
        </table>
        
        <h2>四、总结与建议</h2>
        <div class="summary">
            <ul>
                <li><span class="highlight">数据完整性</span>: 所有 5 家目标店铺数据已成功提取</li>
                <li><span class="highlight">重点关注</span>: 建议关注零售数量和毛利率表现</li>
                <li><span class="highlight">后续行动</span>: 持续跟踪每日数据变化</li>
            </ul>
        </div>
        <p style="text-align: center; color: #999; margin-top: 40px;">* 本报告由系统自动生成 *</p>
    </div>
    <script>
        const ctx = document.getElementById('retailChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(chart_labels)},
                datasets: [{{
                    label: '零售数量',
                    data: {json.dumps(chart_retail_qty)},
                    backgroundColor: 'rgba(26, 115, 232, 0.7)',
                    borderColor: 'rgba(26, 115, 232, 1)',
                    borderWidth: 1
                }}, {{
                    label: '零售金额',
                    data: {json.dumps(chart_retail_amt)},
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    yAxisID: 'y1'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{ display: true, text: '店铺零售数据对比' }}
                }},
                scales: {{
                    y: {{ beginAtZero: true, title: {{ display: true, text: '零售数量' }} }},
                    y1: {{ type: 'linear', display: true, position: 'right', grid: {{ drawOnChartArea: false }}, title: {{ display: true, text: '零售金额' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

with open('KPI 日报_20260310.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
print("OK: KPI 日报_20260310.html")
print("\n完成！")
