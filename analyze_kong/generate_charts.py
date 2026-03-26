#!/usr/bin/env python3
"""
为孔立刚区域分析报告生成图表
"""

import pandas as pd
import sys
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = r"C:\Users\Administrator\.openclaw\workspace\analyze_kong"

# 数据
dealers = ['重庆银马', '重庆万事新', '重庆金团', '重庆瀚达', '西藏鼎恒']
march_target = [763000, 640000, 612600, 337000, 36100]
march_actual = [241684, 106319, 170162, 104572, 0]
march_rate = [31.68, 16.61, 27.78, 31.03, 0.00]
q1_target = [1902200, 1620000, 1527100, 840200, 89900]
q1_actual = [1342632, 1382054, 1081959, 665550, 24247]
q1_rate = [70.58, 85.31, 70.85, 79.21, 26.97]

# ==================== 图表 1: 3 月目标达成率 ====================
fig1 = go.Figure()

fig1.add_trace(go.Bar(
    x=dealers,
    y=march_rate,
    text=[f'{r}%' for r in march_rate],
    textposition='outside',
    marker_color=['#2E86AB' if r >= 25 else '#E94F37' for r in march_rate],
    name='3 月达成率'
))

# 添加时间进度线 (25.8%)
fig1.add_hline(y=25.8, line_dash="dash", line_color="gray", 
               annotation_text="时间进度 25.8%", annotation_position="right")

fig1.update_layout(
    title='📊 3 月零件采购目标达成率 (截至 3 月 8 日)',
    xaxis_title='经销商',
    yaxis_title='达成率 (%)',
    yaxis_range=[0, 100],
    height=400,
    showlegend=False
)

fig1.write_html(f'{OUTPUT_DIR}/chart_march_rate.html', include_plotlyjs='cdn')
print(f'✓ 图表 1 已保存：{OUTPUT_DIR}/chart_march_rate.html')

# ==================== 图表 2: Q1 累计达成率 ====================
fig2 = go.Figure()

fig2.add_trace(go.Bar(
    x=dealers,
    y=q1_rate,
    text=[f'{r}%' for r in q1_rate],
    textposition='outside',
    marker_color=['#28A745' if r >= 70 else '#FFC107' if r >= 50 else '#E94F37' for r in q1_rate],
    name='Q1 达成率'
))

fig2.update_layout(
    title='📈 Q1 累计零件采购目标达成率',
    xaxis_title='经销商',
    yaxis_title='达成率 (%)',
    yaxis_range=[0, 100],
    height=400,
    showlegend=False
)

fig2.write_html(f'{OUTPUT_DIR}/chart_q1_rate.html', include_plotlyjs='cdn')
print(f'✓ 图表 2 已保存：{OUTPUT_DIR}/chart_q1_rate.html')

# ==================== 图表 3: 目标 vs 实际 对比 ====================
fig3 = make_subplots(rows=1, cols=2, subplot_titles=('3 月目标 vs 实际', 'Q1 目标 vs 实际'))

# 3 月
fig3.add_trace(go.Bar(name='目标', x=dealers, y=march_target, marker_color='#6C757D'), row=1, col=1)
fig3.add_trace(go.Bar(name='实际', x=dealers, y=march_actual, marker_color='#2E86AB'), row=1, col=1)

# Q1
fig3.add_trace(go.Bar(name='目标', x=dealers, y=q1_target, marker_color='#6C757D'), row=1, col=2)
fig3.add_trace(go.Bar(name='实际', x=dealers, y=q1_actual, marker_color='#28A745'), row=1, col=2)

fig3.update_layout(
    title='💰 零件采购金额对比 (单位：元)',
    height=450,
    showlegend=True,
    legend=dict(x=0.5, y=1.15, xanchor='center', orientation='h')
)

fig3.update_xaxes(tickangle=45)

fig3.write_html(f'{OUTPUT_DIR}/chart_comparison.html', include_plotlyjs='cdn')
print(f'✓ 图表 3 已保存：{OUTPUT_DIR}/chart_comparison.html')

# ==================== 图表 4: 工单类型分布 ====================
complaint_types = ['车主信息修改', '产品质量抱怨', '经销商服务抱怨', '零件抱怨']
complaint_counts = [7, 4, 5, 1]
complaint_colors = ['#2E86AB', '#E94F37', '#FFC107', '#28A745']

fig4 = go.Figure(data=[go.Pie(
    labels=complaint_types,
    values=complaint_counts,
    marker_colors=complaint_colors,
    textinfo='label+percent+value',
    hole=0.4
)])

fig4.update_layout(
    title='📞 客服工单类型分布 (17 件)',
    height=400
)

fig4.write_html(f'{OUTPUT_DIR}/chart_complaint_types.html', include_plotlyjs='cdn')
print(f'✓ 图表 4 已保存：{OUTPUT_DIR}/chart_complaint_types.html')

# ==================== 图表 5: 经销商工单分布 ====================
dealer_tickets = ['重庆银马', '西藏鼎恒', '重庆万事新', '重庆金团', '重庆瀚达', '其他']
ticket_counts = [5, 4, 3, 1, 1, 3]

fig5 = go.Figure(data=[go.Bar(
    x=dealer_tickets,
    y=ticket_counts,
    text=ticket_counts,
    textposition='outside',
    marker_color='#6C757D'
)])

fig5.update_layout(
    title='🏪 各经销商工单分布',
    xaxis_title='经销商',
    yaxis_title='工单数量',
    height=400,
    showlegend=False
)

fig5.write_html(f'{OUTPUT_DIR}/chart_dealer_tickets.html', include_plotlyjs='cdn')
print(f'✓ 图表 5 已保存：{OUTPUT_DIR}/chart_dealer_tickets.html')

print('\n✅ 所有图表生成完成!')
