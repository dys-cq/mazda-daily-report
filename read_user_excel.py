#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读取参考 Excel 文件的列名和样式"""

import pandas as pd

# 读取参考文件
ref_path = r"C:\Users\Administrator\.openclaw\media\outbound\7edfac85-80ef-49fd-9750-05e75f1c3c3e.xlsx"

# 读取第一个 sheet
df = pd.read_excel(ref_path, sheet_name=0)

print("=" * 80)
print("列名 (Columns):")
print("=" * 80)
for i, col in enumerate(df.columns):
    print(f"{i+1}. {col}")

print("\n" + "=" * 80)
print("第一行数据示例:")
print("=" * 80)
first_row = df.iloc[0].to_dict()
for key, value in first_row.items():
    print(f"{key}: {value}")

print("\n" + "=" * 80)
print("数据结构:")
print("=" * 80)
print(f"总行数：{len(df)}")
print(f"总列数：{len(df.columns)}")
