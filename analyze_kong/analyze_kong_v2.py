#!/usr/bin/env python3
"""
区域经理"孔立刚"数据分析报告
分析零件指标达成和未关闭投诉情况
"""

import pandas as pd
import json
import sys
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# 文件路径
FILE1 = r"C:\Users\Administrator\.openclaw\media\outbound\1530a42b-9e8d-4533-8386-62c974931935.xlsx"  # 投诉数据
FILE2 = r"C:\Users\Administrator\.openclaw\media\outbound\65e7ae84-1b12-4058-8842-8645a0c6c63a.xlsx"  # 零件指标
FILE3 = r"C:\Users\Administrator\.openclaw\media\outbound\e2834bb0-41fd-4758-96bb-dbb839bf3057.xlsx"  # 客服工单

OUTPUT_DIR = r"C:\Users\Administrator\.openclaw\workspace\analyze_kong"

print("="*60)
print("开始分析区域经理'孔立刚'的数据")
print("="*60)

# ==================== 文件 1: 投诉数据 ====================
print("\n【1】加载投诉数据...")
df_complaints = pd.read_excel(FILE1, sheet_name='未撤诉')
print(f"   总投诉记录数：{len(df_complaints)}")

# 查找区域经理列
region_mgr_col = None
dealer_col = None
for col in df_complaints.columns:
    col_str = str(col)
    if '区域经理' in col_str or '经理' in col_str:
        region_mgr_col = col
    if '经销商' in col_str or 'DLR' in col_str:
        dealer_col = col

print(f"   区域经理列：{region_mgr_col}")
print(f"   经销商列：{dealer_col}")

# 筛选孔立刚的数据
df_kong_complaints = df_complaints[df_complaints[region_mgr_col].astype(str).str.contains('孔立刚', na=False)]
print(f"   ✓ 孔立刚的未撤诉投诉数：{len(df_kong_complaints)}")

# ==================== 文件 2: 零件指标数据 ====================
print("\n【2】加载零件指标数据...")

# 读取"零件 - 经销商明细"工作表
df_parts = pd.read_excel(FILE2, sheet_name='零件 - 经销商明细', skiprows=2)
print(f"   总经销商记录数：{len(df_parts)}")

# 查找区域经理列
region_mgr_col_parts = None
for col in df_parts.columns:
    col_str = str(col)
    if '区域经理' in col_str or '经理' in col_str:
        region_mgr_col_parts = col
        break

print(f"   区域经理列：{region_mgr_col_parts}")

# 筛选孔立刚的数据
df_kong_parts = df_parts[df_parts[region_mgr_col_parts].astype(str).str.contains('孔立刚', na=False)]
print(f"   ✓ 孔立刚的经销商数量：{len(df_kong_parts)}")

# 打印孔立刚的零件指标数据
print("\n   孔立刚辖区经销商零件指标详情：")
print(df_kong_parts.to_string())

# ==================== 文件 3: 客服工单 ====================
print("\n【3】加载客服工单数据...")
df_service = pd.read_excel(FILE3, sheet_name='工单 202639101521')
print(f"   总工单数：{len(df_service)}")

# 查找区域经理列
region_mgr_col_service = None
for col in df_service.columns:
    col_str = str(col)
    if '区域经理' in col_str or '经理' in col_str:
        region_mgr_col_service = col
        break

print(f"   区域经理列：{region_mgr_col_service}")

if region_mgr_col_service:
    df_kong_service = df_service[df_service[region_mgr_col_service].astype(str).str.contains('孔立刚', na=False)]
    print(f"   ✓ 孔立刚的工单数：{len(df_kong_service)}")
else:
    df_kong_service = pd.DataFrame()

# ==================== 保存数据 ====================
df_kong_complaints.to_csv(f"{OUTPUT_DIR}/kong_complaints.csv", index=False, encoding='utf-8-sig')
print(f"\n✓ 投诉数据已保存：{OUTPUT_DIR}/kong_complaints.csv")

df_kong_parts.to_csv(f"{OUTPUT_DIR}/kong_parts.csv", index=False, encoding='utf-8-sig')
print(f"✓ 零件指标数据已保存：{OUTPUT_DIR}/kong_parts.csv")

if not df_kong_service.empty:
    df_kong_service.to_csv(f"{OUTPUT_DIR}/kong_service.csv", index=False, encoding='utf-8-sig')
    print(f"✓ 客服工单数据已保存：{OUTPUT_DIR}/kong_service.csv")

print("\n初步分析完成！")
