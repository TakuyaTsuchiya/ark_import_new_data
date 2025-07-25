import pandas as pd
import numpy as np

# Excelファイルの詳細デバッグ
excel_file = r'C:\Users\user04\Downloads\【完全版】一括登録20250617 (2).xlsx'
df = pd.read_excel(excel_file, sheet_name='一括登録で必要なもの', header=None)

print('=== デバッグ: 最初の10行の全データ ===')
print(f'シートサイズ: {df.shape[0]}行 x {df.shape[1]}列')
print()

# 各行の各列を番号付きで詳細表示
for i in range(min(10, len(df))):
    print(f'=== {i+1}行目 ===')
    for j in range(df.shape[1]):
        cell_value = df.iloc[i, j]
        if not pd.isna(cell_value):
            print(f'  列{j}({chr(65+j)}): {str(cell_value)[:100]}')
    print()

print('=== 特にC列（列2）の内容を確認 ===')
for i in range(len(df)):
    c_value = df.iloc[i, 2] if df.shape[1] > 2 else None
    if not pd.isna(c_value) and str(c_value).strip():
        print(f'{i+1}行目のC列: {str(c_value)[:120]}')