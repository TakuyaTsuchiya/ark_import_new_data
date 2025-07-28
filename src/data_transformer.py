"""
データ変換モジュール
"""
import pandas as pd
from typing import Dict, Any, Optional
from config import OUTPUT_COLUMNS, FIXED_VALUES, COLUMN_MAPPINGS, ADDRESS_SPLIT_TARGETS
from utils import (
    remove_fullwidth_space, remove_halfwidth_space, hankaku_to_zenkaku,
    add_leading_zero, normalize_phone_number, format_date,
    calculate_exit_fee, generate_takeover_info, get_today_formatted,
    safe_str_convert, safe_int_convert
)
from address_splitter import AddressSplitter


class DataTransformer:
    """データ変換を行うクラス"""
    
    def __init__(self):
        self.output_columns = OUTPUT_COLUMNS
        self.fixed_values = FIXED_VALUES
        self.column_mappings = COLUMN_MAPPINGS
        self.address_splitter = AddressSplitter()
    
    def create_empty_output_df(self) -> pd.DataFrame:
        """空の出力DataFrameを作成（固定カラム順序で）"""
        # 空文字のカラム名も含めて固定の順序でDataFrameを作成
        data = {col: [] for col in self.output_columns}
        return pd.DataFrame(data)
    
    def apply_transform(self, value: Any, transform: Any) -> Any:
        """変換関数を適用"""
        if transform is None:
            return value
        
        if isinstance(transform, list):
            # 複数の変換を順番に適用
            for t in transform:
                value = self.apply_transform(value, t)
            return value
        
        # 文字列変換
        transform_map = {
            "add_leading_zero": add_leading_zero,
            "remove_fullwidth_space": remove_fullwidth_space,
            "remove_halfwidth_space": remove_halfwidth_space,
            "hankaku_to_zenkaku": hankaku_to_zenkaku,
            "normalize_phone": normalize_phone_number,
            "format_date": format_date
        }
        
        if transform in transform_map:
            return transform_map[transform](safe_str_convert(value))
        
        return value
    
    def process_phone_numbers(self, row: pd.Series) -> Dict[str, str]:
        """電話番号の条件付き処理"""
        home_tel = safe_str_convert(row.get("自宅TEL1", ""))
        mobile_tel = safe_str_convert(row.get("携帯TEL1", ""))
        
        # 電話番号を正規化
        home_tel = normalize_phone_number(home_tel)
        mobile_tel = normalize_phone_number(mobile_tel)
        
        # 自宅TELのみの場合、携帯TELに移動
        if home_tel and not mobile_tel:
            return {"home": "", "mobile": home_tel}
        
        return {"home": home_tel, "mobile": mobile_tel}
    
    def process_guarantor_emergency(self, row: pd.Series) -> Dict[str, Dict[str, str]]:
        """保証人/緊急連絡人の判定と処理"""
        result = {
            "guarantor1": {},
            "emergency1": {}
        }
        
        # 種別／続柄２で判定（部分一致で判定）
        relationship_type = safe_str_convert(row.get("種別／続柄２", ""))
        
        if "保証人" in relationship_type:
            # 保証人情報を設定
            result["guarantor1"] = {
                "氏名": safe_str_convert(row.get("名前2", "")),
                "カナ": hankaku_to_zenkaku(safe_str_convert(row.get("名前2（カナ）", ""))),
                "生年月日": format_date(row.get("生年月日2", "")),
                "郵便番号": "",
                "住所1": "",
                "住所2": "",
                "住所3": "",
                "TEL自宅": normalize_phone_number(safe_str_convert(row.get("自宅TEL2", ""))),
                "TEL携帯": normalize_phone_number(safe_str_convert(row.get("携帯TEL2", "")))
            }
            
            # 住所分割
            address = safe_str_convert(row.get("自宅住所2", ""))
            if address:
                addr_parts = self.address_splitter.split_address(address)
                result["guarantor1"]["郵便番号"] = addr_parts["postal_code"]
                result["guarantor1"]["住所1"] = addr_parts["prefecture"]
                result["guarantor1"]["住所2"] = addr_parts["city"]
                result["guarantor1"]["住所3"] = addr_parts["remainder"]
                
        elif "緊急連絡" in relationship_type:
            # 緊急連絡人情報を設定
            result["emergency1"] = {
                "氏名": safe_str_convert(row.get("名前2", "")),
                "カナ": hankaku_to_zenkaku(safe_str_convert(row.get("名前2（カナ）", ""))),
                "郵便番号": "",
                "住所1": "",
                "住所2": "",
                "住所3": "",
                "TEL自宅": normalize_phone_number(safe_str_convert(row.get("自宅TEL2", ""))),
                "TEL携帯": normalize_phone_number(safe_str_convert(row.get("携帯TEL2", "")))
            }
            
            # 住所分割
            address = safe_str_convert(row.get("自宅住所2", ""))
            if address:
                addr_parts = self.address_splitter.split_address(address)
                result["emergency1"]["郵便番号"] = addr_parts["postal_code"]
                result["emergency1"]["住所1"] = addr_parts["prefecture"]
                result["emergency1"]["住所2"] = addr_parts["city"]
                result["emergency1"]["住所3"] = addr_parts["remainder"]
        
        return result
    
    def transform_row(self, row: pd.Series) -> Dict[str, Any]:
        """1行のデータを変換"""
        output_row = {}
        
        # 固定値を設定
        for col, value in self.fixed_values.items():
            output_row[col] = value
        
        # 基本的なマッピング
        for output_col, mapping in self.column_mappings.items():
            if isinstance(mapping, dict):
                source_col = mapping.get("source")
                transform = mapping.get("transform")
                
                if source_col and source_col in row:
                    value = row[source_col]
                    if transform:
                        value = self.apply_transform(value, transform)
                    output_row[output_col] = safe_str_convert(value)
        
        # 電話番号の条件付き処理
        phone_numbers = self.process_phone_numbers(row)
        output_row["契約者TEL自宅"] = phone_numbers["home"]
        output_row["契約者TEL携帯"] = phone_numbers["mobile"]
        
        # 住所分割処理
        # 契約者現住所（物件住所から生成）
        property_address = safe_str_convert(row.get("物件住所", ""))
        if property_address:
            building_name = safe_str_convert(row.get("物件名", ""))
            room_number = safe_str_convert(row.get("部屋番号", ""))
            addr_parts = self.address_splitter.split_with_building(
                property_address, building_name, room_number
            )
            output_row["契約者現住所郵便番号"] = addr_parts["postal_code"]
            output_row["契約者現住所1"] = addr_parts["prefecture"]
            output_row["契約者現住所2"] = addr_parts["city"]
            output_row["契約者現住所3"] = addr_parts["remainder"]
            
            # 物件住所も分割
            prop_addr_parts = self.address_splitter.split_address(property_address)
            output_row["物件住所郵便番号"] = prop_addr_parts["postal_code"]
            output_row["物件住所1"] = prop_addr_parts["prefecture"]
            output_row["物件住所2"] = prop_addr_parts["city"]
            output_row["物件住所3"] = prop_addr_parts["remainder"]
        
        # 勤務先住所分割
        work_address = safe_str_convert(row.get("勤務先住所1", ""))
        if work_address:
            work_addr_parts = self.address_splitter.split_address(work_address)
            output_row["契約者勤務先郵便番号"] = work_addr_parts["postal_code"]
            output_row["契約者勤務先住所1"] = work_addr_parts["prefecture"]
            output_row["契約者勤務先住所2"] = work_addr_parts["city"]
            output_row["契約者勤務先住所3"] = work_addr_parts["remainder"]
        
        # 保証人/緊急連絡人処理
        guarantor_emergency = self.process_guarantor_emergency(row)
        
        # 保証人１（全角数字）
        if guarantor_emergency["guarantor1"] and guarantor_emergency["guarantor1"].get("氏名"):
            g = guarantor_emergency["guarantor1"]
            output_row["保証人１氏名"] = g["氏名"]
            output_row["保証人１カナ"] = g["カナ"]
            output_row["保証人１契約者との関係"] = "他"  # データがある場合のみ設定
            output_row["保証人１生年月日"] = g["生年月日"]
            output_row["保証人１郵便番号"] = g["郵便番号"]
            output_row["保証人１住所1"] = g["住所1"]
            output_row["保証人１住所2"] = g["住所2"]
            output_row["保証人１住所3"] = g["住所3"]
            output_row["保証人１TEL自宅"] = g["TEL自宅"]
            output_row["保証人１TEL携帯"] = g["TEL携帯"]
        
        # 緊急連絡人１（全角数字）
        if guarantor_emergency["emergency1"] and guarantor_emergency["emergency1"].get("氏名"):
            e = guarantor_emergency["emergency1"]
            output_row["緊急連絡人１氏名"] = e["氏名"]
            output_row["緊急連絡人１カナ"] = e["カナ"]
            output_row["緊急連絡人１契約者との関係"] = "他"  # データがある場合のみ設定
            output_row["緊急連絡人１郵便番号"] = e["郵便番号"]
            output_row["緊急連絡人１住所1"] = e["住所1"]
            output_row["緊急連絡人１住所2"] = e["住所2"]
            output_row["緊急連絡人１住所3"] = e["住所3"]
            output_row["緊急連絡人１TEL自宅"] = e["TEL自宅"]
            output_row["緊急連絡人１TEL携帯"] = e["TEL携帯"]
        
        # 計算フィールド
        # 退去手続き費用
        exit_fee = calculate_exit_fee(
            row.get("賃料", 0),
            row.get("管理共益費", 0),
            row.get("駐車場料金", 0),
            row.get("その他料金", 0)
        )
        output_row["退去手続き（実費）"] = exit_fee
        
        # 管理受託日（今日の日付）
        output_row["管理受託日"] = get_today_formatted()
        
        # 申請者確認日（今日の日付）
        output_row["申請者確認日"] = get_today_formatted()
        
        # 引継情報
        move_in_date = safe_str_convert(row.get("入居日", ""))
        output_row["引継情報"] = generate_takeover_info(move_in_date)
        
        return output_row
    
    def transform_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrameを変換"""
        output_data = []
        
        for idx, row in df.iterrows():
            try:
                transformed_row = self.transform_row(row)
                output_data.append(transformed_row)
            except Exception as e:
                print(f"行 {idx} の変換中にエラー: {e}")
                continue
        
        # 出力DataFrameを作成
        output_df = pd.DataFrame(output_data)
        
        # カラム順序を整える（固定ヘッダーを使用）
        final_data = []
        for idx, row in output_df.iterrows() if not output_df.empty else enumerate([]):
            row_data = []
            for col in self.output_columns:
                if col in output_df.columns:
                    value = row[col] if not pd.isna(row[col]) else ""
                    row_data.append(str(value))
                else:
                    row_data.append("")
            final_data.append(row_data)
        
        # 一時的にカラム名を使用してDataFrameを作成
        temp_columns = [f"col_{i}" for i in range(len(self.output_columns))]
        final_df = pd.DataFrame(final_data, columns=temp_columns)
        
        # 実際のカラム名をセット（pandasの自動リネームを回避）
        final_df.columns = self.output_columns
        
        print(f"変換完了: {len(final_df)}件のレコード")
        
        return final_df