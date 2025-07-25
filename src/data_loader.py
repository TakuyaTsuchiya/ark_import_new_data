"""
データ読み込みモジュール
"""
import pandas as pd
import glob
import os
from pathlib import Path
from typing import Tuple, Optional
import chardet


class DataLoader:
    """CSVファイルの読み込みを管理するクラス"""
    
    def __init__(self, encoding: str = "cp932"):
        self.encoding = encoding
    
    def detect_encoding(self, file_path: str) -> str:
        """ファイルのエンコーディングを検出"""
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            return result['encoding']
    
    def load_csv(self, file_path: str, encoding: Optional[str] = None) -> pd.DataFrame:
        """CSVファイルを読み込む"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        
        # エンコーディングが指定されていない場合はデフォルトを使用
        if encoding is None:
            encoding = self.encoding
        
        try:
            # まずは指定されたエンコーディングで読み込み
            return pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError:
            # エラーが発生した場合は、エンコーディングを検出して再試行
            detected_encoding = self.detect_encoding(file_path)
            print(f"エンコーディングエラー。{detected_encoding}で再試行します。")
            return pd.read_csv(file_path, encoding=detected_encoding)
    
    def find_latest_file(self, pattern: str, directory: str = ".") -> Optional[str]:
        """
        パターンに一致する最新のファイルを検索
        
        Args:
            pattern: ファイル名のパターン（例: "【東京支店】①案件取込用レポート*.csv"）
            directory: 検索ディレクトリ
            
        Returns:
            最新ファイルのパス、見つからない場合はNone
        """
        search_pattern = os.path.join(directory, pattern)
        files = glob.glob(search_pattern)
        
        if not files:
            return None
        
        # ファイルを更新時刻でソート（最新が最後）
        files.sort(key=lambda x: os.path.getmtime(x))
        return files[-1]
    
    def load_input_files(self, 
                        report_path: Optional[str] = None,
                        contract_list_path: Optional[str] = None,
                        downloads_dir: str = r"C:\Users\user04\Downloads") -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        入力ファイルを読み込む
        
        Args:
            report_path: 案件取込用レポートのパス（Noneの場合は自動検索）
            contract_list_path: ContractListのパス（Noneの場合は自動検索）
            downloads_dir: ダウンロードディレクトリ
            
        Returns:
            (案件取込用レポート, ContractList) のDataFrameタプル
        """
        # 案件取込用レポートを読み込み
        if report_path is None:
            report_path = self.find_latest_file(
                "【東京支店】①案件取込用レポート*.csv",
                downloads_dir
            )
            if report_path is None:
                raise FileNotFoundError(
                    f"案件取込用レポートが見つかりません。{downloads_dir}に配置してください。"
                )
            print(f"案件取込用レポートを検出: {os.path.basename(report_path)}")
        
        # ContractListを読み込み
        if contract_list_path is None:
            contract_list_path = self.find_latest_file(
                "ContractList_*.csv",
                downloads_dir
            )
            if contract_list_path is None:
                raise FileNotFoundError(
                    f"ContractListが見つかりません。{downloads_dir}に配置してください。"
                )
            print(f"ContractListを検出: {os.path.basename(contract_list_path)}")
        
        # ファイルを読み込み
        print("ファイルを読み込み中...")
        report_df = self.load_csv(report_path)
        contract_list_df = self.load_csv(contract_list_path)
        
        print(f"案件取込用レポート: {len(report_df)}件")
        print(f"ContractList: {len(contract_list_df)}件")
        
        return report_df, contract_list_df
    
    def load_sample_output(self, sample_path: Optional[str] = None,
                          downloads_dir: str = r"C:\Users\user04\Downloads") -> Optional[pd.DataFrame]:
        """
        サンプル出力ファイルを読み込む（カラム構造の参照用）
        
        Args:
            sample_path: サンプルファイルのパス
            downloads_dir: ダウンロードディレクトリ
            
        Returns:
            サンプルのDataFrame、見つからない場合はNone
        """
        if sample_path is None:
            sample_path = os.path.join(downloads_dir, "ContractInfoSample（final）.csv")
        
        if os.path.exists(sample_path):
            print(f"サンプルファイルを読み込み: {os.path.basename(sample_path)}")
            return self.load_csv(sample_path)
        
        return None