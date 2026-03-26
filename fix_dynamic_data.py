with open('build_final_report_v7.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 添加查找最新售后日报文件的逻辑
old_import = "import os, pandas as pd, json, shutil, html, glob"
new_import = """import os, pandas as pd, json, shutil, html, glob
from datetime import datetime, timedelta"""

content = content.replace(old_import, new_import)

# 2. 替换硬编码的 CSV 路径为动态查找 Excel
old_biz_start = """# biz minimal - 从 sheet_3 和 sheet_2 获取数据
biz_metrics={}
biz_csv='C:/Users/Administrator/.openclaw/workspace/sheet_3_3 月 mazda.csv'
biz_detail_csv=glob.glob('sheet_2*.csv')[0] if glob.glob('sheet_2*.csv') else None
biz_detail_df=pd.read_csv(biz_detail_csv) if biz_detail_csv else None
if os.path.exists(biz_csv):
    biz_df=pd.read_csv(biz_csv)"""

new_biz_start = """# biz minimal - 直接从 E:/2026 年 KPI 目录读取最新售后日报 Excel
biz_metrics={}

# 查找最新售后日报文件
def find_latest_aftermarket_report(base_dir):
    \"\"\"查找最新的售后日报 Excel 文件\"\"\"
    candidates=[]
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if '售后' in f and f.endswith('.xlsx') and not f.startswith('~$'):
                full=os.path.join(root,f)
                candidates.append((full, os.path.getmtime(full)))
    if candidates:
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    return None

aftermarket_file = find_latest_aftermarket_report('E:/2026 年 KPI')
biz_detail_df=None
biz_df=None

if aftermarket_file:
    print(f'使用售后日报文件：{aftermarket_file}')
    try:
        xl=pd.ExcelFile(aftermarket_file)
        # 读取综合日报 sheet（通常是第一个或包含"综合"的 sheet）
        for sn in xl.sheet_names:
            if '综合' in sn or '日报' in sn or sn=='Sheet1':
                biz_df=pd.read_excel(aftermarket_file, sheet_name=sn)
                break
        # 读取零附件明细 sheet
        for sn in xl.sheet_names:
            if '零附件' in sn or '附件' in sn:
                biz_detail_df=pd.read_excel(aftermarket_file, sheet_name=sn)
                break
        if biz_df is None and xl.sheet_names:
            biz_df=pd.read_excel(aftermarket_file, sheet_name=xl.sheet_names[0])
    except Exception as e:
        print(f'读取售后日报失败：{e}')
        biz_df=None
        biz_detail_df=None
else:
    print('未找到售后日报文件')

# 如果有售后日报，从中提取数据；否则回退到 CSV
if biz_df is not None and not biz_df.empty:
    for st in stores:
        code=store_codes[st]"""

content = content.replace(old_biz_start, new_biz_start)

# 3. 修改循环结构
old_loop = """if os.path.exists(biz_csv):
    biz_df=pd.read_csv(biz_csv)
    for st in stores:
        code=store_codes[st]
        row=biz_df[biz_df.iloc[:,0].astype(str)==code]
        m={}
        if not row.empty:
            r=row.iloc[0]
            cols=r.index
            def find_any(keys):
                for c in cols:
                    if any(k in str(c) for k in keys):
                        return r[c]
                return None
            # 辅助函数：百分比格式化
            def fmt_pct(val):
                if val is None or str(val)=='nan' or val=='':
                    return None
                try:
                    f=float(val)
                    if 0 <= f <= 1:
                        return f"{f*100:.2f}%"
                    return f"{f:.2f}%"
                except:
                    return str(val)
            
            # 计算机油单车和事故单车
            oil_value = float(r.iloc[20]) if pd.notna(r.iloc[20]) else 0
            accident_value = float(r.iloc[11]) if pd.notna(r.iloc[11]) else 0
            deal_count = float(r.iloc[93]) if pd.notna(r.iloc[93]) else 1
            accident_count = float(r.iloc[79]) if pd.notna(r.iloc[79]) else 1"""

new_loop = """# 已在上面处理"""

# 只替换一次
if old_loop in content:
    content = content.replace(old_loop, new_loop, 1)

with open('build_final_report_v7.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
