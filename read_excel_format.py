#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读取用户提供的 Excel 文件格式"""

import pandas as pd

# 读取用户提供的 Excel 文件
input_path = r"C:\Users\Administrator\.openclaw\media\outbound\7edfac85-80ef-49fd-9750-05e75f1c3c3e.xlsx"

# 读取 Excel
df = pd.read_excel(input_path)

# 打印列名
print("列名:")
print(df.columns.tolist())

# 打印前几行数据
print("\n前 5 行数据:")
print(df.head())

# 打印所有数据
print("\n完整数据:")
print(df.to_string())
