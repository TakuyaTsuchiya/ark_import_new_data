"""
実際のファイルのカラム名を調査
"""
import pandas as pd
from data_loader import DataLoader

def main():
    # データローダーを初期化
    loader = DataLoader()
    
    try:
        # ファイルを読み込み
        report_df, contract_list_df = loader.load_input_files()
        
        print("=== 案件取込用レポートのカラム名 ===")
        for i, col in enumerate(report_df.columns):
            print(f"{i:2d}: {col}")
        
        print(f"\n総カラム数: {len(report_df.columns)}")
        
        # 最初の5行を確認
        print("\n=== 最初の5行のデータ ===")
        print(report_df.head())
        
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    main()