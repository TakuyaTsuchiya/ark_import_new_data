import pandas as pd
import numpy as np

# Excelファイルの詳細読み込み
excel_file = r'C:\Users\user04\Downloads\【完全版】一括登録20250617 (2).xlsx'
df = pd.read_excel(excel_file, header=None)

print('=== 加工ルール詳細確認（全列表示） ===')
print(f'シート全体: {df.shape[0]}行 x {df.shape[1]}列')
print()

# 各行の全列を確認
for i in range(min(40, len(df))):
    has_data = False
    row_data = []
    
    for j in range(df.shape[1]):
        cell_value = df.iloc[i, j] if not pd.isna(df.iloc[i, j]) else ''
        if str(cell_value).strip() and 'nan' not in str(cell_value):
            has_data = True
            row_data.append(f'列{chr(65+j)}({j}): {str(cell_value)[:100]}')
    
    if has_data:
        print(f'{i+1:2d}行目:')
        for data in row_data:
            print(f'   {data}')
        print()