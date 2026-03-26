import pandas as pd
import glob
import os
import sys

# 设置输出编码
sys.stdout.reconfigure(encoding='utf-8')

# 列出所有 CSV 文件
csv_files = glob.glob('sheet_*.csv')
print(f"CSV files: {csv_files}")

# 目标店铺
target_stores = ['重庆金团', '重庆瀚达', '重庆银马', '重庆万事新', '西藏鼎恒']

# 读取经销商映射表 (sheet_9_Sheet3.csv - 第 2 大文件)
print("\n=== Dealer Map ===")
df_map = pd.read_csv('sheet_9_Sheet3.csv')
print(f"Shape: {df_map.shape}")
print(f"Cols: {list(df_map.columns)[:5]}")

# 第二列应该是经销商名称
dealer_name_col = df_map.columns[1]
print(f"Dealer name col: {dealer_name_col}")

# 查找目标店铺
print("\n=== Finding target stores ===")
store_codes = {}
for store in target_stores:
    mask = df_map[dealer_name_col].astype(str).str.contains(store, na=False)
    if mask.any():
        matching = df_map[mask]
        code = matching.iloc[0, 0]
        name = matching.iloc[0, 1]
        print(f"OK {store}: code={code}, name={name}")
        store_codes[store] = code
    else:
        print(f"NOT FOUND: {store}")

print(f"\nStore codes: {store_codes}")

# 读取 3 月 mazda 数据 (最大的 CSV 文件)
print("\n=== Reading Mazda data ===")
mazda_file = max(csv_files, key=lambda f: os.path.getsize(f))
print(f"File: {mazda_file}")
mazda_df = pd.read_csv(mazda_file)
print(f"Shape: {mazda_df.shape}")

# 第一列是经销商代码
dealer_code_col = mazda_df.columns[0]
print(f"Dealer code col: {dealer_code_col}")

# 筛选目标店铺数据
print("\n=== Filtering store data ===")
store_data = {}
for store, code in store_codes.items():
    mask = mazda_df[dealer_code_col] == code
    if mask.any():
        print(f"OK {store} ({code}): {mask.sum()} records")
        store_data[store] = mazda_df[mask].copy()
    else:
        print(f"NO DATA: {store} ({code})")

# 保存结果
print("\n=== Saving results ===")
for store, df in store_data.items():
    outfile = f'{store}_data.csv'
    df.to_csv(outfile, index=False, encoding='utf-8-sig')
    print(f"{store}: {len(df)} records -> {outfile}")

# 汇总统计
print("\n=== Summary ===")
if store_data:
    combined = pd.concat(store_data.values(), keys=store_data.keys())
    combined.to_csv('all_target_stores.csv', index=False, encoding='utf-8-sig')
    print(f"Total records: {len(combined)}")
    print("Saved to all_target_stores.csv")
