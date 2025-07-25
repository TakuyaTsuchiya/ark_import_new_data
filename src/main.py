"""
アーク新規登録データ変換ツール
メイン処理モジュール
"""
import sys
import os
import argparse
from datetime import datetime
from data_loader import DataLoader
from data_validator import DataValidator
from data_transformer import DataTransformer
from data_exporter import DataExporter
from config import get_config


def print_header():
    """ヘッダー情報を表示"""
    print("=" * 60)
    print("アーク新規登録データ変換ツール")
    print("=" * 60)
    print(f"実行日時: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
    print()


def main():
    """メイン処理"""
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(
        description="アーク新規登録用のデータ変換ツール"
    )
    parser.add_argument(
        "--report", 
        help="案件取込用レポートのパス",
        default=None
    )
    parser.add_argument(
        "--contract-list", 
        help="ContractListのパス",
        default=None
    )
    parser.add_argument(
        "--output", 
        help="出力ファイルのパス",
        default=None
    )
    parser.add_argument(
        "--downloads-dir", 
        help="ダウンロードディレクトリ",
        default=r"C:\Users\user04\Downloads"
    )
    parser.add_argument(
        "--output-dir", 
        help="出力ディレクトリ",
        default="."
    )
    parser.add_argument(
        "--skip-report", 
        help="処理レポートの生成をスキップ",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # ヘッダー表示
    print_header()
    
    # 設定を取得
    config = get_config()
    
    try:
        # 1. データ読み込み
        print("【ステップ1】データ読み込み")
        print("-" * 40)
        
        loader = DataLoader(encoding=config["encoding"])
        report_df, contract_list_df = loader.load_input_files(
            report_path=args.report,
            contract_list_path=args.contract_list,
            downloads_dir=args.downloads_dir
        )
        
        # 2. データ検証
        print("\n【ステップ2】データ検証")
        print("-" * 40)
        
        validator = DataValidator()
        validated_df, validation_summary = validator.validate_all(
            report_df, contract_list_df
        )
        
        if len(validated_df) == 0:
            print("\n警告: 有効なレコードがありません。処理を終了します。")
            return 1
        
        # 3. データ変換
        print("\n【ステップ3】データ変換")
        print("-" * 40)
        
        transformer = DataTransformer()
        output_df = transformer.transform_dataframe(validated_df)
        
        # 4. データ出力
        print("\n【ステップ4】データ出力")
        print("-" * 40)
        
        exporter = DataExporter(encoding=config["encoding"])
        output_path = exporter.export_to_csv(
            output_df,
            output_path=args.output,
            output_dir=args.output_dir
        )
        
        # 5. レポート生成（オプション）
        if not args.skip_report:
            print("\n【ステップ5】レポート生成")
            print("-" * 40)
            
            # エラーログ出力
            if validation_summary.get("error_log"):
                exporter.export_error_log(
                    validation_summary["error_log"],
                    output_dir=args.output_dir
                )
            
            # 処理レポート生成
            exporter.create_summary_report(
                output_df,
                validation_summary,
                output_dir=args.output_dir
            )
        
        print("\n" + "=" * 60)
        print("処理が正常に完了しました！")
        print("=" * 60)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\nエラー: {e}")
        print("必要なファイルが見つかりません。ファイルパスを確認してください。")
        return 1
        
    except Exception as e:
        print(f"\n予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())