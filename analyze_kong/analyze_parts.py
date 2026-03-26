#!/usr/bin/env python3
"""
区域经理"孔立刚"数据深度分析
生成图文并茂的分析报告
"""

import pandas as pd
import sys
import json
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

FILE2 = r"C:\Users\Administrator\.openclaw\media\outbound\65e7ae84-1b12-4058-8842-8645a0c6c63a.xlsx"
OUTPUT_DIR = r"C:\Users\Administrator\.openclaw\workspace\analyze_kong"

print("分析零件指标数据...")

# 读取零件 - 经销商明细 (索引 2)
df_parts = pd.read_excel(FILE2, sheet_name=2, skiprows=2)
print(f"总记录数：{len(df_parts)}")
print(f"列名：{list(df_parts.columns)}")

# 查找孔立刚的数据（根据之前分析，区域经理在第 8 列索引）
# 从之前输出看到：['A13314', '海口优之杰汽车服务有限公司', '海口优之杰', '海南省', '海口市', '海口优之杰.1', '正常', '南区', '宋扬', ...]
# 第 8 列 (索引 8) 是区域经理

# 检查第 8 列
print(f"\n第 8 列唯一值样本：{df_parts.iloc[:, 8].unique()[:10]}")

# 筛选孔立刚
df_kong = df_parts[df_parts.iloc[:, 8].astype(str).str.contains('孔立刚', na=False)]
print(f"\n孔立刚的经销商数量：{len(df_kong)}")
print(f"\n孔立刚辖区经销商数据：")
print(df_kong.to_string())

# 保存
df_kong.to_csv(f"{OUTPUT_DIR}/kong_parts_full.csv", index=False, encoding='utf-8-sig')
print(f"\n数据已保存：{OUTPUT_DIR}/kong_parts_full.csv")
