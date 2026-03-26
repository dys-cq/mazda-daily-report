#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读取参考 Excel 文件格式"""

import pandas as pd

# 读取最新的参考文件
input_path = r"C:\Users\Administrator\.openclaw\workspace\OpenClaw 技能管理表_已更新.xlsx"

# 读取 Excel
df = pd.read_excel(input_path)

# 打印列名
print("列名:")
print(df.columns.tolist())

# 打印前 3 行数据
print("\n前 3 行数据:")
print(df.head(3).to_string())
