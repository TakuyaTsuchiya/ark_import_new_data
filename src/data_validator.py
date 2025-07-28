"""
データ検証モジュール
"""
import pandas as pd
from datetime import datetime
from typing import List, Tuple, Dict, Any
from config import VALIDATION_RULES


class DataValidator:
    """データの検証を行うクラス"""
    
    def __init__(self):
        self.rules = VALIDATION_RULES
        self.error_log = []
    
    def validate_birthdate(self, date_str: str) -> bool:
        """
        生年月日の妥当性を検証
        
        Args:
            date_str: 生年月日文字列
            
        Returns:
            妥当な場合True
        """
        if not date_str:
            return True  # 空の場合は許可
        
        try:
            # 様々な日付フォーマットを試す
            date_formats = ["%Y/%m/%d", "%Y-%m-%d", "%Y年%m月%d日"]
            date_obj = None
            
            for fmt in date_formats:
                try:
                    date_obj = datetime.strptime(str(date_str), fmt)
                    break
                except ValueError:
                    continue
            
            if date_obj is None:
                return False
            
            # 年が最小年以降かチェック
            return date_obj.year >= self.rules["birthdate_min_year"]
            
        except Exception:
            return False
    
    def check_duplicates(self, report_df: pd.DataFrame, 
                        contract_list_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        重複チェックを実行
        
        Args:
            report_df: 案件取込用レポートのDataFrame
            contract_list_df: ContractListのDataFrame
            
        Returns:
            (重複を除外したDataFrame, 除外された契約番号リスト)
        """
        # ContractListの引継番号リストを取得
        existing_numbers = set()
        if "引継番号" in contract_list_df.columns:
            existing_numbers = set(contract_list_df["引継番号"].dropna().astype(str))
        
        # 案件取込用レポートの契約番号をチェック
        duplicates = []
        keep_indices = []
        
        for idx, row in report_df.iterrows():
            contract_number = str(row.get("契約番号", ""))
            
            # 先頭に0を付けた番号でチェック
            if contract_number:
                check_number = "0" + contract_number
                if check_number in existing_numbers:
                    duplicates.append(contract_number)
                else:
                    keep_indices.append(idx)
            else:
                keep_indices.append(idx)
        
        if duplicates:
            print(f"重複データを{len(duplicates)}件除外しました")
            for num in duplicates[:5]:  # 最初の5件を表示
                print(f"  - 契約番号: {num}")
            if len(duplicates) > 5:
                print(f"  ... 他{len(duplicates) - 5}件")
        
        # 重複を除外したDataFrameを返す
        filtered_df = report_df.loc[keep_indices].reset_index(drop=True)
        
        return filtered_df, duplicates
    
    def validate_required_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        必須フィールドの検証
        
        Args:
            df: 検証するDataFrame
            
        Returns:
            有効なレコードのみのDataFrame
        """
        required_fields = self.rules["required_fields"]
        
        # 必須フィールドが存在するかチェック
        missing_columns = []
        for field in required_fields:
            if field not in df.columns:
                missing_columns.append(field)
        
        if missing_columns:
            raise ValueError(f"必須カラムが不足しています: {missing_columns}")
        
        # 必須フィールドが空でないレコードのみ抽出
        valid_mask = pd.Series([True] * len(df))
        invalid_records = []
        
        for field in required_fields:
            field_mask = df[field].notna() & (df[field] != "")
            invalid_indices = df[~field_mask].index
            
            for idx in invalid_indices:
                if idx not in invalid_records:
                    invalid_records.append(idx)
                    self.error_log.append({
                        "index": idx,
                        "field": field,
                        "reason": "必須フィールドが空"
                    })
            
            valid_mask &= field_mask
        
        if invalid_records:
            print(f"必須フィールドが空のレコードを{len(invalid_records)}件除外しました")
        
        return df[valid_mask].reset_index(drop=True)
    
    def validate_birthdates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        生年月日の検証と修正
        
        Args:
            df: 検証するDataFrame
            
        Returns:
            異常な生年月日を空白に修正したDataFrame（レコード自体は保持）
        """
        # 生年月日カラムを特定
        birthdate_columns = [col for col in df.columns if "生年月日" in col]
        
        # DataFrameのコピーを作成（元のデータを変更しないため）
        df_corrected = df.copy()
        corrected_records = []
        
        for idx, row in df_corrected.iterrows():
            # 主契約者の生年月日をチェック
            if "生年月日1" in df_corrected.columns:
                main_birthdate = row.get("生年月日1", "")
                if main_birthdate and not self.validate_birthdate(main_birthdate):
                    # 異常な生年月日を空白に修正
                    df_corrected.at[idx, "生年月日1"] = ""
                    corrected_records.append({
                        "index": idx,
                        "contract_number": row.get("契約番号", ""),
                        "original_birthdate": main_birthdate,
                        "field": "生年月日1"
                    })
            
            # その他の生年月日カラムもチェック（生年月日2など）
            for col in birthdate_columns:
                if col != "生年月日1" and col in df_corrected.columns:
                    birthdate_value = row.get(col, "")
                    if birthdate_value and not self.validate_birthdate(birthdate_value):
                        # 異常な生年月日を空白に修正
                        df_corrected.at[idx, col] = ""
                        corrected_records.append({
                            "index": idx,
                            "contract_number": row.get("契約番号", ""),
                            "original_birthdate": birthdate_value,
                            "field": col
                        })
        
        if corrected_records:
            print(f"異常な生年月日を持つ{len(corrected_records)}件のフィールドを空白に修正しました")
            for record in corrected_records:  # 全件表示
                print(f"  - 契約番号: {record['contract_number']}, 元の値: {record['original_birthdate']}, フィールド: {record['field']}")
        
        return df_corrected
    
    def validate_all(self, report_df: pd.DataFrame, 
                    contract_list_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        すべての検証を実行
        
        Args:
            report_df: 案件取込用レポートのDataFrame
            contract_list_df: ContractListのDataFrame
            
        Returns:
            (検証済みDataFrame, 検証結果サマリー)
        """
        self.error_log = []
        original_count = len(report_df)
        
        # 1. 必須フィールドの検証
        validated_df = self.validate_required_fields(report_df)
        
        # 2. 生年月日の検証
        validated_df = self.validate_birthdates(validated_df)
        
        # 3. 重複チェック
        validated_df, duplicates = self.check_duplicates(validated_df, contract_list_df)
        
        # 検証結果サマリー
        summary = {
            "original_count": original_count,
            "validated_count": len(validated_df),
            "excluded_count": original_count - len(validated_df),
            "duplicate_count": len(duplicates),
            "error_log": self.error_log
        }
        
        print(f"\n検証結果サマリー:")
        print(f"  元のレコード数: {summary['original_count']}")
        print(f"  有効レコード数: {summary['validated_count']}")
        print(f"  除外レコード数: {summary['excluded_count']}")
        
        return validated_df, summary