#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import sys
import os

def analyze_csv_files():
    """2つのCSVファイルを比較分析する"""
    
    # ファイルパス
    generated_file = r"C:\Users\user04\Desktop\ark_import_new_data\0725アーク新規登録.csv"
    template_file = r"C:\Users\user04\Downloads\新規登録アーク0723.csv"
    
    print("=" * 80)
    print("CSVファイル比較分析レポート")
    print("=" * 80)
    
    # エンコーディングのリスト
    encodings = ['utf-8', 'shift_jis', 'cp932', 'utf-8-sig']
    
    # 生成ファイルの読み込み
    df_generated = None
    generated_encoding = None
    for encoding in encodings:
        try:
            df_generated = pd.read_csv(generated_file, encoding=encoding)
            generated_encoding = encoding
            print(f"✓ 生成ファイルを{encoding}で読み込み成功")
            break
        except Exception as e:
            continue
    
    if df_generated is None:
        print("✗ 生成ファイルの読み込みに失敗")
        return
    
    # お手本ファイルの読み込み
    df_template = None
    template_encoding = None
    for encoding in encodings:
        try:
            df_template = pd.read_csv(template_file, encoding=encoding)
            template_encoding = encoding
            print(f"✓ お手本ファイルを{encoding}で読み込み成功")
            break
        except Exception as e:
            continue
    
    if df_template is None:
        print("✗ お手本ファイルの読み込みに失敗")
        return
    
    print("\n" + "=" * 50)
    print("1. 基本情報の比較")
    print("=" * 50)
    
    print(f"生成ファイル:")
    print(f"  - ファイル名: 0725アーク新規登録.csv")
    print(f"  - エンコーディング: {generated_encoding}")
    print(f"  - 行数: {len(df_generated)} データ行")
    print(f"  - 列数: {len(df_generated.columns)} 列")
    
    print(f"\nお手本ファイル:")
    print(f"  - ファイル名: 新規登録アーク0723.csv")
    print(f"  - エンコーディング: {template_encoding}")
    print(f"  - 行数: {len(df_template)} データ行")
    print(f"  - 列数: {len(df_template.columns)} 列")
    
    print(f"\n列数の差: {len(df_template.columns) - len(df_generated.columns)} 列")
    
    print("\n" + "=" * 50)
    print("2. ヘッダー列名の比較")
    print("=" * 50)
    
    generated_cols = set(df_generated.columns)
    template_cols = set(df_template.columns)
    
    # 共通列
    common_cols = generated_cols & template_cols
    print(f"共通列数: {len(common_cols)}")
    
    # 生成ファイルにのみ存在する列
    only_in_generated = generated_cols - template_cols
    if only_in_generated:
        print(f"\n生成ファイルのみに存在する列 ({len(only_in_generated)}個):")
        for col in sorted(only_in_generated):
            print(f"  - {col}")
    
    # お手本ファイルにのみ存在する列
    only_in_template = template_cols - generated_cols
    if only_in_template:
        print(f"\nお手本ファイルのみに存在する列 ({len(only_in_template)}個):")
        for col in sorted(only_in_template):
            print(f"  - {col}")
    
    print("\n" + "=" * 50)
    print("3. NAN/NULL値の分析")
    print("=" * 50)
    
    print("生成ファイルのNAN値統計:")
    generated_nulls = df_generated.isnull().sum()
    non_zero_nulls_gen = generated_nulls[generated_nulls > 0]
    if len(non_zero_nulls_gen) > 0:
        for col, count in non_zero_nulls_gen.head(10).items():
            print(f"  - {col}: {count} NAN値")
    else:
        print("  - NAN値なし")
    
    print(f"\nお手本ファイルのNAN値統計:")
    template_nulls = df_template.isnull().sum()
    non_zero_nulls_temp = template_nulls[template_nulls > 0]
    if len(non_zero_nulls_temp) > 0:
        for col, count in non_zero_nulls_temp.head(10).items():
            print(f"  - {col}: {count} NAN値")
    else:
        print("  - NAN値なし")
    
    print("\n" + "=" * 50)
    print("4. 共通列のデータ型比較")
    print("=" * 50)
    
    type_differences = []
    for col in sorted(common_cols)[:10]:  # 最初の10列のみ表示
        gen_type = str(df_generated[col].dtype)
        temp_type = str(df_template[col].dtype)
        if gen_type != temp_type:
            type_differences.append((col, gen_type, temp_type))
            print(f"型の違い - {col}:")
            print(f"  生成: {gen_type}")
            print(f"  お手本: {temp_type}")
    
    if not type_differences:
        print("主要列のデータ型は一致しています")
    
    print("\n" + "=" * 50)
    print("5. サンプルデータの比較（最初の3行）")
    print("=" * 50)
    
    # 共通の最初の5列を表示
    common_first_cols = []
    for col in df_template.columns[:5]:
        if col in df_generated.columns:
            common_first_cols.append(col)
    
    if common_first_cols:
        print("生成ファイルのサンプルデータ:")
        print(df_generated[common_first_cols].head(3).to_string(index=False))
        
        print("\nお手本ファイルのサンプルデータ:")
        print(df_template[common_first_cols].head(3).to_string(index=False))
    
    print("\n" + "=" * 50)
    print("6. 特殊値の分析")
    print("=" * 50)
    
    # "nan"文字列の検索
    print("'nan'文字列の検出:")
    gen_nan_strings = 0
    temp_nan_strings = 0
    
    for col in df_generated.columns:
        if df_generated[col].dtype == 'object':
            nan_count = (df_generated[col].astype(str).str.lower() == 'nan').sum()
            gen_nan_strings += nan_count
    
    for col in df_template.columns:
        if df_template[col].dtype == 'object':
            nan_count = (df_template[col].astype(str).str.lower() == 'nan').sum()
            temp_nan_strings += nan_count
    
    print(f"  生成ファイル: {gen_nan_strings} 個の'nan'文字列")
    print(f"  お手本ファイル: {temp_nan_strings} 個の'nan'文字列")
    
    print("\n" + "=" * 50)
    print("7. 主要な問題点まとめ")
    print("=" * 50)
    
    issues = []
    
    if len(only_in_template) > 0:
        issues.append(f"・お手本ファイルに存在するが生成ファイルにない列が{len(only_in_template)}個あります")
    
    if len(only_in_generated) > 0:
        issues.append(f"・生成ファイルに余分な列が{len(only_in_generated)}個あります")
    
    if gen_nan_strings > temp_nan_strings:
        issues.append(f"・生成ファイルに'nan'文字列が多く含まれています（差分: {gen_nan_strings - temp_nan_strings}個）")
    
    if type_differences:
        issues.append(f"・データ型が異なる列が{len(type_differences)}個あります")
    
    if len(df_generated) != len(df_template):
        issues.append(f"・データ行数が異なります（生成: {len(df_generated)}行, お手本: {len(df_template)}行）")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("重大な問題は検出されませんでした。")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    analyze_csv_files()