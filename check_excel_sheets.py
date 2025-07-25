import pandas as pd
import numpy as np

# Excelファイルの全シート確認
excel_file = r'C:\Users\user04\Downloads\【完全版】一括登録20250617 (2).xlsx'

# 全シート名を取得
excel_file_obj = pd.ExcelFile(excel_file)
sheet_names = excel_file_obj.sheet_names

print('=== Excelファイルのシート一覧 ===')
for i, sheet_name in enumerate(sheet_names):
    print(f'{i+1}. {sheet_name}')

print()

# 各シートの内容を確認
for sheet_name in sheet_names[:3]:  # 最初の3シートのみ確認
    print(f'=== シート: {sheet_name} ===')
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
    print(f'サイズ: {df.shape[0]}行 x {df.shape[1]}列')
    
    # 最初の10行を確認
    for i in range(min(10, len(df))):
        row_data = []
        for j in range(min(6, df.shape[1])):  # 最初の6列のみ確認
            cell_value = df.iloc[i, j] if not pd.isna(df.iloc[i, j]) else ''
            if str(cell_value).strip():
                row_data.append(f'{chr(65+j)}列: {str(cell_value)[:50]}')
        
        if row_data:
            print(f'  {i+1}行目: {" | ".join(row_data)}')
    print()