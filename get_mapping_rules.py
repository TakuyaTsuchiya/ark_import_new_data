import pandas as pd
import numpy as np

# 一括登録で必要なものシートを詳しく確認
excel_file = r'C:\Users\user04\Downloads\【完全版】一括登録20250617 (2).xlsx'
df = pd.read_excel(excel_file, sheet_name='一括登録で必要なもの', header=None)

print('=== 一括登録で必要なもの シート詳細 ===')
print(f'サイズ: {df.shape[0]}行 x {df.shape[1]}列')
print()

# 全行を詳しく確認してマッピング情報を抽出
print('=== 元データ → アークテンプレートのマッピング ===')
for i in range(len(df)):
    col_a = df.iloc[i, 0] if not pd.isna(df.iloc[i, 0]) else ''  # 新規案件情報CSV
    col_c = df.iloc[i, 2] if df.shape[1] > 2 and not pd.isna(df.iloc[i, 2]) else ''  # アークデータ
    col_f = df.iloc[i, 5] if df.shape[1] > 5 and not pd.isna(df.iloc[i, 5]) else ''  # 注意点備考
    
    # データがある行のみ表示
    if str(col_a).strip() or str(col_c).strip():
        print(f'{i+1:2d}行目:')
        if str(col_a).strip():
            print(f'   新規案件CSV: {str(col_a)[:120]}')
        if str(col_c).strip():
            print(f'   アークデータ: {str(col_c)[:120]}')
        if str(col_f).strip():
            print(f'   注意点備考 : {str(col_f)[:120]}')
        print()

# P列（15列目）もチェック
print('=== P列（対応フィールド名）も確認 ===')
for i in range(len(df)):
    col_p = df.iloc[i, 15] if df.shape[1] > 15 and not pd.isna(df.iloc[i, 15]) else ''
    if str(col_p).strip():
        col_a = df.iloc[i, 0] if not pd.isna(df.iloc[i, 0]) else ''
        print(f'{i+1:2d}行目: 元データ=「{str(col_a)[:50]}」 → アークフィールド=「{str(col_p)[:50]}」')