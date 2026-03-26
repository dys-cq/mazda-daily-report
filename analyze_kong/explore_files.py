import pandas as pd
import os

files = [
    r"C:\Users\Administrator\.openclaw\media\outbound\1530a42b-9e8d-4533-8386-62c974931935.xlsx",
    r"C:\Users\Administrator\.openclaw\media\outbound\65e7ae84-1b12-4058-8842-8645a0c6c63a.xlsx",
    r"C:\Users\Administrator\.openclaw\media\outbound\e2834bb0-41fd-4758-96bb-dbb839bf3057.xlsx"
]

for i, f in enumerate(files, 1):
    print(f"\n{'='*60}")
    print(f"文件 {i}: {os.path.basename(f)}")
    print('='*60)
    try:
        xls = pd.ExcelFile(f)
        print(f"工作表：{xls.sheet_names}")
        for sheet in xls.sheet_names:
            df = pd.read_excel(f, sheet_name=sheet, nrows=5)
            print(f"\n--- 工作表：{sheet} ---")
            print(f"列名：{list(df.columns)}")
            print(f"前 5 行数据：")
            print(df.to_string())
    except Exception as e:
        print(f"错误：{e}")
