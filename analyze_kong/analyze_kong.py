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
try:
    df_complaints = pd.read_excel(FILE1, sheet_name='未关闭')
    print(f"   总投诉记录数：{len(df_complaints)}")
    print(f"   列名：{list(df_complaints.columns)}")
    
    # 查找区域经理列
    region_mgr_col = None
    for col in df_complaints.columns:
        if '区域经理' in str(col) or '经理' in str(col):
            region_mgr_col = col
            break
    
    if region_mgr_col:
        print(f"   区域经理列：{region_mgr_col}")
        # 筛选孔立刚的数据
        df_kong_complaints = df_complaints[df_complaints[region_mgr_col].astype(str).str.contains('孔立刚', na=False)]
        print(f"   孔立刚的未关闭投诉数：{len(df_kong_complaints)}")
    else:
        print("   ⚠️ 未找到区域经理列，尝试按其他方式筛选...")
        df_kong_complaints = pd.DataFrame()
        
except Exception as e:
    print(f"   ❌ 错误：{e}")
    df_kong_complaints = pd.DataFrame()

# ==================== 文件 2: 零件指标数据 ====================
print("\n【2】加载零件指标数据...")
try:
    xls = pd.ExcelFile(FILE2)
    print(f"   工作表：{xls.sheet_names}")
    
    # 查找包含区域经理数据的工作表
    df_kong_parts = None
    
    # 尝试"汇总 - 经销商详情"工作表
    if '汇总 - 经销商详情' in xls.sheet_names:
        df_detail = pd.read_excel(FILE2, sheet_name='汇总 - 经销商详情', skiprows=2)
        print(f"   '汇总 - 经销商详情' 列名：{list(df_detail.columns)}")
        
        # 查找区域经理列
        region_mgr_col = None
        for col in df_detail.columns:
            if '区域经理' in str(col) or '经理' in str(col):
                region_mgr_col = col
                break
        
        if region_mgr_col:
            df_kong_parts = df_detail[df_detail[region_mgr_col].astype(str).str.contains('孔立刚', na=False)]
            print(f"   孔立刚的经销商数量：{len(df_kong_parts)}")
            print(f"   孔立刚的区域经理列：{region_mgr_col}")
            
except Exception as e:
    print(f"   ❌ 错误：{e}")

# ==================== 文件 3: 客服工单 ====================
print("\n【3】加载客服工单数据...")
try:
    df_service = pd.read_excel(FILE3, sheet_name='客服 202639101521')
    print(f"   总工单数：{len(df_service)}")
    
    # 查找区域经理列
    region_mgr_col = None
    for col in df_service.columns:
        if '区域经理' in str(col) or '经理' in str(col):
            region_mgr_col = col
            break
    
    if region_mgr_col:
        df_kong_service = df_service[df_service[region_mgr_col].astype(str).str.contains('孔立刚', na=False)]
        print(f"   孔立刚的工单数：{len(df_kong_service)}")
    else:
        df_kong_service = pd.DataFrame()
        
except Exception as e:
    print(f"   ❌ 错误：{e}")
    df_kong_service = pd.DataFrame()

# ==================== 生成摘要 ====================
print("\n" + "="*60)
print("分析摘要")
print("="*60)

summary = {
    "区域经理": "孔立刚",
    "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "未关闭投诉数": len(df_kong_complaints) if not df_kong_complaints.empty else 0,
    "经销商数量": len(df_kong_parts) if df_kong_parts is not None else 0,
    "客服工单数": len(df_kong_service) if not df_kong_service.empty else 0,
}

print(json.dumps(summary, ensure_ascii=False, indent=2))

# 保存中间数据供后续使用
if not df_kong_complaints.empty:
    df_kong_complaints.to_csv(f"{OUTPUT_DIR}/kong_complaints.csv", index=False, encoding='utf-8-sig')
    print(f"\n✓ 投诉数据已保存：{OUTPUT_DIR}/kong_complaints.csv")

if df_kong_parts is not None and not df_kong_parts.empty:
    df_kong_parts.to_csv(f"{OUTPUT_DIR}/kong_parts.csv", index=False, encoding='utf-8-sig')
    print(f"✓ 零件指标数据已保存：{OUTPUT_DIR}/kong_parts.csv")

if not df_kong_service.empty:
    df_kong_service.to_csv(f"{OUTPUT_DIR}/kong_service.csv", index=False, encoding='utf-8-sig')
    print(f"✓ 客服工单数据已保存：{OUTPUT_DIR}/kong_service.csv")

print("\n分析完成！")
