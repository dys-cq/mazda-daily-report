import pandas as pd
import glob

files = glob.glob(r'E:\2026*KPI\*20260310*')
print(f"Files: {files}")

if files:
    main_file = files[0]
    xl = pd.ExcelFile(main_file)
    print(f"Sheets ({len(xl.sheet_names)}): {xl.sheet_names}")
    
    # Try reading by index
    print("\n=== Reading sheet by index ===")
    for i, sheet in enumerate(xl.sheet_names):
        print(f"\nSheet {i}: {sheet}")
        try:
            df = pd.read_excel(main_file, sheet_name=i)
            print(f"  Shape: {df.shape}")
            print(f"  First col: {df.columns[0] if len(df.columns) > 0 else 'N/A'}")
            if len(df) > 0:
                print(f"  First value: {df.iloc[0, 0]}")
            
            # Save large sheets
            if len(df) > 100:
                df.to_csv(f'sheet_{i}_{sheet[:20]}.csv', index=False, encoding='utf-8-sig')
                print(f"  Saved to sheet_{i}.csv")
        except Exception as e:
            print(f"  Error: {e}")
