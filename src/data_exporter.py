"""
データ出力モジュール
"""
import pandas as pd
import os
import csv
from datetime import datetime
from typing import Optional
from utils import get_output_filename

# テンプレートファイルから直接ヘッダーを読み取る
def get_template_headers():
    """テンプレートファイルから正確なヘッダーを取得（Unnamedカラムを空文字に変換）"""
    template_path = r"C:\Users\user04\Downloads\ContractInfoSample（final） (2).csv"
    try:
        df = pd.read_csv(template_path, encoding='cp932', nrows=0)
        headers = df.columns.tolist()
        
        # Unnamedカラムを空文字に変換
        cleaned_headers = []
        for header in headers:
            if 'Unnamed:' in str(header):
                cleaned_headers.append("")
            else:
                cleaned_headers.append(header)
        
        return cleaned_headers
    except Exception as e:
        print(f"テンプレートファイル読み込みエラー: {e}")
        # フォールバック（緊急時用）
        from config import OUTPUT_COLUMNS
        return OUTPUT_COLUMNS


class DataExporter:
    """データの出力を管理するクラス"""
    
    def __init__(self, encoding: str = "cp932"):
        self.encoding = encoding
    
    def export_to_csv(self, df: pd.DataFrame, 
                     output_path: Optional[str] = None,
                     output_dir: str = ".") -> str:
        """
        DataFrameをCSVファイルに出力（固定ヘッダーを使用）
        
        Args:
            df: 出力するDataFrame
            output_path: 出力ファイルパス（Noneの場合は自動生成）
            output_dir: 出力ディレクトリ
            
        Returns:
            出力したファイルのパス
        """
        # 出力ファイル名を決定
        if output_path is None:
            filename = get_output_filename()
            output_path = os.path.join(output_dir, filename)
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        try:
            # 固定ヘッダーを使用してCSVに出力
            self._write_csv_with_fixed_header(df, output_path)
            
            print(f"\nファイルを出力しました: {output_path}")
            print(f"レコード数: {len(df)}件")
            print(f"カラム数: {len(get_template_headers())}列")
            
            # ファイルサイズを表示
            file_size = os.path.getsize(output_path)
            if file_size > 1024 * 1024:
                print(f"ファイルサイズ: {file_size / (1024 * 1024):.2f} MB")
            else:
                print(f"ファイルサイズ: {file_size / 1024:.2f} KB")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"ファイル出力エラー: {e}")
    
    def _write_csv_with_fixed_header(self, df: pd.DataFrame, output_path: str):
        """
        固定ヘッダーを使用してCSVファイルを書き込み（テンプレートから直接取得）
        
        Args:
            df: 出力するDataFrame
            output_path: 出力ファイルパス
        """
        # テンプレートから正確なヘッダーを取得
        template_headers = get_template_headers()
        
        with open(output_path, 'w', newline='', encoding=self.encoding) as csvfile:
            writer = csv.writer(csvfile)
            
            # テンプレートの正確なヘッダーを書き込み
            writer.writerow(template_headers)
            
            # データ行を書き込み
            for _, row in df.iterrows():
                data_row = []
                for col in template_headers:
                    if col in df.columns:
                        value = row[col]
                        # NaNや空文字は空文字に統一
                        try:
                            if pd.isna(value) or value is None or value == "":
                                data_row.append("")
                            elif isinstance(value, pd.Series):
                                # Seriesオブジェクトの場合は最初の値を取得
                                data_row.append(str(value.iloc[0]) if len(value) > 0 and not pd.isna(value.iloc[0]) else "")
                            else:
                                data_row.append(str(value))
                        except (TypeError, ValueError, AttributeError):
                            # その他のエラーは空文字として処理
                            data_row.append("")
                    else:
                        data_row.append("")
                writer.writerow(data_row)
    
    def export_error_log(self, error_log: list, 
                        output_dir: str = ".") -> Optional[str]:
        """
        エラーログをファイルに出力
        
        Args:
            error_log: エラーログのリスト
            output_dir: 出力ディレクトリ
            
        Returns:
            出力したファイルのパス（エラーがない場合はNone）
        """
        if not error_log:
            return None
        
        # エラーログファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_file = os.path.join(output_dir, f"error_log_{timestamp}.txt")
        
        try:
            with open(error_file, "w", encoding="utf-8") as f:
                f.write("データ変換エラーログ\n")
                f.write("=" * 50 + "\n")
                f.write(f"生成日時: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                
                for i, error in enumerate(error_log, 1):
                    f.write(f"エラー {i}:\n")
                    for key, value in error.items():
                        f.write(f"  {key}: {value}\n")
                    f.write("\n")
            
            print(f"\nエラーログを出力しました: {error_file}")
            return error_file
            
        except Exception as e:
            print(f"エラーログ出力失敗: {e}")
            return None
    
    def create_summary_report(self, df: pd.DataFrame, 
                            validation_summary: dict,
                            output_dir: str = ".") -> str:
        """
        処理サマリーレポートを作成
        
        Args:
            df: 出力データ
            validation_summary: 検証結果サマリー
            output_dir: 出力ディレクトリ
            
        Returns:
            レポートファイルのパス
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(output_dir, f"processing_report_{timestamp}.txt")
        
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write("アーク新規登録データ変換 処理レポート\n")
                f.write("=" * 60 + "\n")
                f.write(f"処理日時: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                
                f.write("【処理結果サマリー】\n")
                f.write(f"元データレコード数: {validation_summary.get('original_count', 0)}件\n")
                f.write(f"除外レコード数: {validation_summary.get('excluded_count', 0)}件\n")
                f.write(f"  - 重複による除外: {validation_summary.get('duplicate_count', 0)}件\n")
                f.write(f"  - 検証エラーによる除外: {validation_summary.get('excluded_count', 0) - validation_summary.get('duplicate_count', 0)}件\n")
                f.write(f"出力レコード数: {len(df)}件\n\n")
                
                f.write("【出力ファイル情報】\n")
                f.write(f"ファイル名: {get_output_filename()}\n")
                f.write(f"カラム数: {len(df.columns)}列\n")
                f.write(f"エンコーディング: {self.encoding}\n\n")
                
                # 金額情報のサマリー
                if "月額賃料" in df.columns:
                    f.write("【金額情報サマリー】\n")
                    numeric_columns = ["月額賃料", "管理費", "駐車場代", "その他費用1", "その他費用2", "管理前滞納額"]
                    for col in numeric_columns:
                        if col in df.columns:
                            # 数値に変換してから計算
                            numeric_series = pd.to_numeric(df[col], errors='coerce').fillna(0)
                            total = numeric_series.sum()
                            avg = numeric_series.mean()
                            f.write(f"{col}: 合計 {total:,.0f}円, 平均 {avg:,.0f}円\n")
                
            print(f"\n処理レポートを出力しました: {report_file}")
            return report_file
            
        except Exception as e:
            print(f"レポート出力失敗: {e}")
            return None