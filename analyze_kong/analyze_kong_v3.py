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

# ==================== 文件 1: 投诉数据 (索引 0 = '未撤诉') ====================
print("\n【1】加载投诉数据...")
df_complaints = pd.read_excel(FILE1, sheet_name=0)
print(f"   总投诉记录数：{len(df_complaints)}")

# 打印列名以便查找
print(f"   列名：{list(df_complaints.columns)}")

# 查找区域经理列
region_mgr_col = None
dealer_col = None
for col in df_complaints.columns:
    col_str = str(col)
    if '经理' in col_str:
        region_mgr_col = col
    if 'DLR' in col_str or '经销商' in col_str:
        dealer_col = col

print(f"   区域经理列：{region_mgr_col}")
print(f"   经销商列：{dealer_col}")

# 筛选孔立刚的数据
if region_mgr_col:
    df_kong_complaints = df_complaints[df_complaints[region_mgr_col].astype(str).str.contains('孔立刚', na=False)]
    print(f"   ✓ 孔立刚的未撤诉投诉数：{len(df_kong_complaints)}")
    if not df_kong_complaints.empty:
        print(f"   投诉详情:\n{df_kong_complaints.to_string()}")
else:
    df_kong_complaints = pd.DataFrame()

# ==================== 文件 2: 零件指标数据 (索引 2 = '零件 - 经销商明细') ====================
print("\n【2】加载零件指标数据...")

# 使用索引读取
df_parts = pd.read_excel(FILE2, sheet_name=2, skiprows=2)
print(f"   总经销商记录数：{len(df_parts)}")
print(f"   前 5 行列名：{list(df_parts.columns[:15])}...")

# 查找区域经理列
region_mgr_col_parts = None
dealer_name_col = None
for col in df_parts.columns:
    col_str = str(col)
    if '经理' in col_str:
        region_mgr_col_parts = col
    if '经销商' in col_str or '名称' in col_str:
        dealer_name_col = col

print(f"   区域经理列：{region_mgr_col_parts}")
print(f"   经销商名称列：{dealer_name_col}")

# 筛选孔立刚的数据
if region_mgr_col_parts:
    df_kong_parts = df_parts[df_parts[region_mgr_col_parts].astype(str).str.contains('孔立刚', na=False)]
    print(f"   ✓ 孔立刚的经销商数量：{len(df_kong_parts)}")
    
    if not df_kong_parts.empty:
        print("\n   孔立刚辖区经销商零件指标详情：")
        # 选择关键列显示
        display_cols = [c for c in df_kong_parts.columns if any(k in str(c) for k in ['经销商','名称','经理','采购','达成','目标','实际'])]
        if not display_cols:
            display_cols = list(df_kong_parts.columns[:15])
        print(df_kong_parts[display_cols].to_string())
else:
    df_kong_parts = pd.DataFrame()

# ==================== 文件 3: 客服工单 (索引 0) ====================
print("\n【3】加载客服工单数据...")
df_service = pd.read_excel(FILE3, sheet_name=0)
print(f"   总工单数：{len(df_service)}")

# 查找区域经理列
region_mgr_col_service = None
for col in df_service.columns:
    col_str = str(col)
    if '经理' in col_str:
        region_mgr_col_service = col
        break

print(f"   区域经理列：{region_mgr_col_service}")

if region_mgr_col_service:
    df_kong_service = df_service[df_service[region_mgr_col_service].astype(str).str.contains('孔立刚', na=False)]
    print(f"   ✓ 孔立刚的工单数：{len(df_kong_service)}")
    if not df_kong_service.empty:
        print(f"   工单详情:\n{df_kong_service.to_string()}")
else:
    df_kong_service = pd.DataFrame()

# ==================== 保存数据 ====================
if not df_kong_complaints.empty:
    df_kong_complaints.to_csv(f"{OUTPUT_DIR}/kong_complaints.csv", index=False, encoding='utf-8-sig')
    print(f"\n✓ 投诉数据已保存：{OUTPUT_DIR}/kong_complaints.csv")

if not df_kong_parts.empty:
    df_kong_parts.to_csv(f"{OUTPUT_DIR}/kong_parts.csv", index=False, encoding='utf-8-sig')
    print(f"✓ 零件指标数据已保存：{OUTPUT_DIR}/kong_parts.csv")

if not df_kong_service.empty:
    df_kong_service.to_csv(f"{OUTPUT_DIR}/kong_service.csv", index=False, encoding='utf-8-sig')
    print(f"✓ 客服工单数据已保存：{OUTPUT_DIR}/kong_service.csv")

print("\n初步分析完成！")
