"""
住所分割モジュール
"""
import re
from typing import Dict, Optional, Tuple
from config import PREFECTURES
from utils import extract_postal_code


class AddressSplitter:
    """住所を構成要素に分割するクラス"""
    
    def __init__(self):
        self.prefectures = PREFECTURES
        self.city_patterns = [
            r"(.+?[市町村])",  # 市町村
            r"(.+?郡.+?[町村])",  # 郡町村
            r"(.+?区)",  # 区（東京23区など）
        ]
    
    def split_address(self, address: str) -> Dict[str, str]:
        """
        住所を郵便番号、都道府県、市区町村、それ以降に分割
        
        Args:
            address: 分割する住所文字列
            
        Returns:
            分割された住所の辞書
        """
        if not address:
            return {
                "postal_code": "",
                "prefecture": "",
                "city": "",
                "remainder": ""
            }
        
        # 郵便番号を抽出
        postal_code = extract_postal_code(address)
        
        # 郵便番号を除去した住所
        clean_address = address
        if postal_code:
            # 郵便番号とその前後の記号を除去
            patterns = [
                f"〒?{postal_code}",
                f"〒?{postal_code.replace('-', '')}",
            ]
            for pattern in patterns:
                clean_address = re.sub(pattern, "", clean_address).strip()
        
        # 都道府県を抽出
        prefecture = ""
        remainder = clean_address
        
        for pref in self.prefectures:
            if clean_address.startswith(pref):
                prefecture = pref
                remainder = clean_address[len(pref):]
                break
        
        # 市区町村を抽出
        city = ""
        city_remainder = remainder
        
        if remainder:
            # 東京23区の特別処理
            if prefecture == "東京都":
                special_wards = [
                    "千代田区", "中央区", "港区", "新宿区", "文京区", "台東区",
                    "墨田区", "江東区", "品川区", "目黒区", "大田区", "世田谷区",
                    "渋谷区", "中野区", "杉並区", "豊島区", "北区", "荒川区",
                    "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区"
                ]
                for ward in special_wards:
                    if remainder.startswith(ward):
                        city = ward
                        city_remainder = remainder[len(ward):]
                        break
            
            # 通常の市区町村パターン
            if not city:
                for pattern in self.city_patterns:
                    match = re.match(pattern, remainder)
                    if match:
                        city = match.group(1)
                        city_remainder = remainder[len(city):]
                        break
        
        return {
            "postal_code": postal_code,
            "prefecture": prefecture,
            "city": city,
            "remainder": city_remainder.strip()
        }
    
    def split_with_building(self, address: str, building_name: str = "", room_number: str = "") -> Dict[str, str]:
        """
        住所を分割し、建物名と部屋番号を結合
        
        Args:
            address: 分割する住所文字列
            building_name: 建物名
            room_number: 部屋番号
            
        Returns:
            分割された住所の辞書
        """
        result = self.split_address(address)
        
        # remainder に建物名と部屋番号を追加
        if result["remainder"]:
            parts = [result["remainder"]]
            if building_name:
                parts.append(building_name)
            if room_number:
                parts.append(room_number)
            result["remainder"] = "　".join(parts)
        else:
            parts = []
            if building_name:
                parts.append(building_name)
            if room_number:
                parts.append(room_number)
            if parts:
                result["remainder"] = "　".join(parts)
        
        return result
    
    def format_address_for_output(self, address_dict: Dict[str, str]) -> Tuple[str, str, str, str]:
        """
        分割された住所を出力用にフォーマット
        
        Returns:
            (郵便番号, 都道府県, 市区町村, それ以降)
        """
        return (
            address_dict.get("postal_code", ""),
            address_dict.get("prefecture", ""),
            address_dict.get("city", ""),
            address_dict.get("remainder", "")
        )