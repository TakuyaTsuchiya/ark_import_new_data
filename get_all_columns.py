import pandas as pd
import numpy as np

# 一括登録で必要なものシートを詳しく確認 - 全列表示
excel_file = r'C:\Users\user04\Downloads\【完全版】一括登録20250617 (2).xlsx'
df = pd.read_excel(excel_file, sheet_name='一括登録で必要なもの', header=None)

print('=== 一括登録で必要なもの シート - 全列表示 ===')
print(f'サイズ: {df.shape[0]}行 x {df.shape[1]}列')
print()

# 各行の全列を表示（データがある列のみ）
for i in range(len(df)):
    row_has_data = False
    row_display = []
    
    for j in range(df.shape[1]):
        cell_value = df.iloc[i, j] if not pd.isna(df.iloc[i, j]) else ''
        if str(cell_value).strip():
            row_has_data = True
            col_letter = chr(65 + j) if j < 26 else f'A{chr(65 + j - 26)}'
            row_display.append(f'{col_letter}列: {str(cell_value)[:80]}')
    
    if row_has_data:
        print(f'{i+1:2d}行目:')
        for col_data in row_display:
            print(f'   {col_data}')
        print()
        
        # 重要そうな行（マッピング関係）は特に詳細表示
        if i <= 20:  # 最初の20行は詳細表示
            continue