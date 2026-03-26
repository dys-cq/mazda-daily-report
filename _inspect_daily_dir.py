import pandas as pd, os
base = r'E:\每日分析数据源'
out = []
out.append('files: ' + repr(os.listdir(base)))
for f in os.listdir(base):
    p = os.path.join(base, f)
    out.append(f'\n=== {f} ===')
    if f.lower().endswith(('.xlsx', '.xls')):
        try:
            xl = pd.ExcelFile(p)
            out.append('sheets: ' + repr(xl.sheet_names))
            for s in xl.sheet_names[:4]:
                df = pd.read_excel(p, sheet_name=s, nrows=5)
                out.append(f'sheet {s} cols: {repr(list(df.columns))}')
                out.append(df.head(2).to_string())
        except Exception as e:
            out.append('excel err ' + repr(e))
    else:
        try:
            tables = pd.read_html(p)
            out.append('html tables: ' + str(len(tables)))
            for i, t in enumerate(tables[:2]):
                out.append(f'table {i} shape {t.shape}')
                out.append(t.head(2).to_string())
        except Exception as e:
            out.append('html err ' + repr(e))
open('_inspect_daily_dir_output.txt','w',encoding='utf-8').write('\n'.join(out))
print('WROTE _inspect_daily_dir_output.txt')
