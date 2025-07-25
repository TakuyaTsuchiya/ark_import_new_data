#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

def detailed_column_analysis():
    """詳細な列構造の分析"""
    
    # ファイルパス
    generated_file = r"C:\Users\user04\Desktop\ark_import_new_data\0725アーク新規登録.csv"
    template_file = r"C:\Users\user04\Downloads\新規登録アーク0723.csv"
    
    # ファイル読み込み
    df_generated = pd.read_csv(generated_file, encoding='cp932')
    df_template = pd.read_csv(template_file, encoding='cp932')
    
    print("=" * 80)
    print("詳細な列構造分析")
    print("=" * 80)
    
    print("\n=== 生成ファイルの列一覧 ===")
    for i, col in enumerate(df_generated.columns, 1):
        print(f"{i:3d}. {col}")
    
    print(f"\n=== お手本ファイルの列一覧 ===")
    for i, col in enumerate(df_template.columns, 1):
        print(f"{i:3d}. {col}")
    
    # 列の位置対応表を作成
    print("\n" + "=" * 80)
    print("列の対応関係分析")
    print("=" * 80)
    
    # 共通列の位置比較
    common_cols = set(df_generated.columns) & set(df_template.columns)
    print(f"\n共通列の位置比較 (共通列数: {len(common_cols)}):")
    
    position_differences = []
    for col in sorted(common_cols)[:20]:  # 最初の20列のみ表示
        gen_pos = list(df_generated.columns).index(col) + 1
        temp_pos = list(df_template.columns).index(col) + 1
        if gen_pos != temp_pos:
            position_differences.append((col, gen_pos, temp_pos))
            print(f"位置違い - {col}: 生成({gen_pos}) vs お手本({temp_pos})")
    
    if not position_differences:
        print("主要列の位置は一致しています")
    
    # 特定の重要な列の詳細分析
    print("\n" + "=" * 80)
    print("重要列の詳細分析")
    print("=" * 80)
    
    important_cols = ['利用者番号', '申請者氏名', '申請者カナ', '申請者生年月日', 
                     '申請者TEL番号', '申請者住所郵便番号', '管理会社', '保証人1氏名']
    
    for col in important_cols:
        print(f"\n--- {col} ---")
        if col in df_generated.columns and col in df_template.columns:
            gen_sample = df_generated[col].head(3).tolist()
            temp_sample = df_template[col].head(3).tolist()
            print(f"生成ファイル: {gen_sample}")
            print(f"お手本ファイル: {temp_sample}")
            
            # NAN値の比較
            gen_nan = df_generated[col].isnull().sum()
            temp_nan = df_template[col].isnull().sum()
            print(f"NAN値 - 生成: {gen_nan}, お手本: {temp_nan}")
        elif col in df_generated.columns:
            print("生成ファイルのみに存在")
        elif col in df_template.columns:
            print("お手本ファイルのみに存在")
        else:
            print("両方に存在しません")
    
    # 文字列"nan"の詳細分析
    print("\n" + "=" * 80)
    print("'nan'文字列の詳細分析")
    print("=" * 80)
    
    print("\n生成ファイルで'nan'文字列を含む列:")
    gen_nan_cols = []
    for col in df_generated.columns:
        if df_generated[col].dtype == 'object':
            nan_count = (df_generated[col].astype(str).str.lower() == 'nan').sum()
            if nan_count > 0:
                gen_nan_cols.append((col, nan_count))
    
    for col, count in sorted(gen_nan_cols, key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {col}: {count}個")
    
    print("\nお手本ファイルで'nan'文字列を含む列:")
    temp_nan_cols = []
    for col in df_template.columns:
        if df_template[col].dtype == 'object':
            nan_count = (df_template[col].astype(str).str.lower() == 'nan').sum()
            if nan_count > 0:
                temp_nan_cols.append((col, nan_count))
    
    for col, count in sorted(temp_nan_cols, key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {col}: {count}個")

if __name__ == "__main__":
    detailed_column_analysis()