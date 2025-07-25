import pandas as pd
import numpy as np

# Excelファイルの詳細読み込み
excel_file = r'C:\Users\user04\Downloads\【完全版】一括登録20250617 (2).xlsx'
df = pd.read_excel(excel_file, header=None)

print('=== 加工ルール詳細確認 ===')
print(f'シート全体: {df.shape[0]}行 x {df.shape[1]}列')
print()

# 各行を詳しく確認
print('=== マッピングルール ===')
for i in range(min(100, len(df))):
    col_a = df.iloc[i, 0] if not pd.isna(df.iloc[i, 0]) else ''
    col_c = df.iloc[i, 2] if df.shape[1] > 2 and not pd.isna(df.iloc[i, 2]) else ''
    col_f = df.iloc[i, 5] if df.shape[1] > 5 and not pd.isna(df.iloc[i, 5]) else ''
    
    # 空行をスキップしつつ、重要な情報のみ表示
    if str(col_a).strip() and 'nan' not in str(col_a):
        print(f'{i+1:2d}行目:')
        print(f'   新規案件情報CSV: {str(col_a)[:150]}')
        if str(col_c).strip() and 'nan' not in str(col_c):
            print(f'   アークデータ     : {str(col_c)[:150]}')
        if str(col_f).strip() and 'nan' not in str(col_f):
            print(f'   注意点備考       : {str(col_f)[:150]}')
        print()