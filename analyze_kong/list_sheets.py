import pandas as pd
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

FILE1 = r"C:\Users\Administrator\.openclaw\media\outbound\1530a42b-9e8d-4533-8386-62c974931935.xlsx"
FILE2 = r"C:\Users\Administrator\.openclaw\media\outbound\65e7ae84-1b12-4058-8842-8645a0c6c63a.xlsx"
FILE3 = r"C:\Users\Administrator\.openclaw\media\outbound\e2834bb0-41fd-4758-96bb-dbb839bf3057.xlsx"

print("文件 1 工作表:")
xls1 = pd.ExcelFile(FILE1)
for i, sheet in enumerate(xls1.sheet_names):
    print(f"  [{i}] {repr(sheet)}")

print("\n文件 2 工作表:")
xls2 = pd.ExcelFile(FILE2)
for i, sheet in enumerate(xls2.sheet_names):
    print(f"  [{i}] {repr(sheet)}")

print("\n文件 3 工作表:")
xls3 = pd.ExcelFile(FILE3)
for i, sheet in enumerate(xls3.sheet_names):
    print(f"  [{i}] {repr(sheet)}")
