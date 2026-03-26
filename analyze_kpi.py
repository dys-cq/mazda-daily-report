import os
import pandas as pd
import glob

# 使用通配符查找文件
files = glob.glob(r'E:\2026*KPI\*20260310*')
print(f"找到文件：{files}")

if files:
    main_file = files[0]
    print(f"\n读取：{main_file}")
    
    xl = pd.ExcelFile(main_file)
    print(f"Sheets: {xl.sheet_names}")
    
    # 目标店铺
    target_stores = ['重庆金团', '重庆瀚达', '重庆银马', '重庆万事新', '西藏鼎恒']
    
    # 读取 3 月 mazda sheet
    if '3 月 mazda' in xl.sheet_names:
        print("\n=== 读取 3 月 mazda ===")
        try:
            df = pd.read_excel(main_file, sheet_name='3 月 mazda')
            print(f"形状：{df.shape}")
            print(f"前 10 列：{list(df.columns)[:10]}")
            
            # 第一列通常是经销商代码
            first_col = df.columns[0]
            print(f"\n第一列：{first_col}")
            print(f"前 20 个值：{df[first_col].head(20).tolist()}")
            
            # 保存所有数据
            df.to_csv('all_dealer_data.csv', index=False, encoding='utf-8-sig')
            print(f"\n已保存所有数据 ({len(df)} 条) 到 all_dealer_data.csv")
            
            # 查找目标店铺
            print("\n=== 查找目标店铺 ===")
            store_results = {}
            for store in target_stores:
                for col in df.columns:
                    mask = df[col].astype(str).str.contains(store, na=False)
                    if mask.any():
                        print(f"✓ {store}: 在列 '{col}' 中找到 {mask.sum()} 条")
                        store_results[store] = df[mask].copy()
                        break
                if store not in store_results:
                    print(f"✗ {store}: 未找到")
            
            # 保存结果
            if store_results:
                all_results = []
                for store, df_store in store_results.items():
                    df_store['目标店铺'] = store
                    all_results.append(df_store)
                combined = pd.concat(all_results, ignore_index=True)
                combined.to_csv('target_stores_data.csv', index=False, encoding='utf-8-sig')
                print(f"\n已保存目标店铺数据 ({len(combined)} 条) 到 target_stores_data.csv")
                
        except Exception as e:
            print(f"错误：{e}")
            import traceback
            traceback.print_exc()
