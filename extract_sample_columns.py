"""
お手本ファイルの列構造を抽出
"""
import pandas as pd

def main():
    # お手本ファイルを読み込み
    sample_df = pd.read_csv(r"C:\Users\user04\Downloads\新規登録アーク0723.csv", encoding="cp932")
    
    print("=== お手本ファイルの列構造 ===")
    print(f"カラム数: {len(sample_df.columns)}")
    print()
    
    # Python配列として出力
    print("OUTPUT_COLUMNS = [")
    for i, col in enumerate(sample_df.columns):
        print(f'    "{col}",  # {i+1}')
    print("]")
    
    # 不要そうな列をチェック
    print("\n=== 空の列（不要可能性あり） ===")
    for col in sample_df.columns:
        if sample_df[col].isna().all() or (sample_df[col] == "").all():
            print(f"- {col}")

if __name__ == "__main__":
    main()