"""
ユーティリティ関数モジュール
"""
import re
import unicodedata
import pandas as pd
from datetime import datetime
from typing import Optional, Union


def remove_fullwidth_space(text: str) -> str:
    """全角スペースを除去"""
    if not text:
        return text
    return text.replace("　", "")


def remove_all_spaces(text: str) -> str:
    """全角・半角スペースを全て除去"""
    if not text:
        return text
    return text.replace("　", "").replace(" ", "")


def remove_halfwidth_space(text: str) -> str:
    """半角スペースを除去"""
    if not text:
        return text
    return text.replace(" ", "")


def hankaku_to_zenkaku(text: str) -> str:
    """半角カナを全角カナに変換"""
    if not text:
        return text
    return unicodedata.normalize('NFKC', text)


def add_leading_zero(text: str) -> str:
    """先頭に0を追加"""
    if not text:
        return text
    return "0" + str(text)


def extract_postal_code(address: str) -> str:
    """住所から郵便番号を抽出"""
    if not address:
        return ""
    
    # 〒マークがある場合
    if "〒" in address:
        address = address.split("〒")[1]
    
    # 郵便番号パターン（XXX-XXXX）
    pattern = r"(\d{3}[-－ー]\d{4})"
    match = re.search(pattern, address)
    if match:
        return match.group(1).replace("－", "-").replace("ー", "-")
    
    # 郵便番号パターン（XXXXXXX）
    pattern = r"(\d{7})"
    match = re.search(pattern, address)
    if match:
        postal = match.group(1)
        return f"{postal[:3]}-{postal[3:]}"
    
    return ""


def normalize_phone_number(phone: str) -> str:
    """電話番号を正規化"""
    if not phone:
        return ""
    
    # 全角数字を半角に変換
    phone = unicodedata.normalize('NFKC', phone)
    
    # 記号を統一
    phone = phone.replace("－", "-").replace("ー", "-").replace("‐", "-")
    phone = phone.replace("（", "(").replace("）", ")")
    
    # 不要な文字を除去
    phone = re.sub(r"[^\d\-\(\)]", "", phone)
    
    return phone


def format_date(date_str: str, output_format: str = "%Y/%m/%d") -> str:
    """日付を指定フォーマットに変換"""
    if not date_str:
        return ""
    
    # 既に正しいフォーマットの場合
    if re.match(r"\d{4}/\d{2}/\d{2}", str(date_str)):
        return date_str
    
    # 様々な日付フォーマットを試す
    date_formats = [
        "%Y-%m-%d",
        "%Y年%m月%d日",
        "%Y.%m.%d",
        "%Y/%m/%d",
        "%Y%m%d"
    ]
    
    for fmt in date_formats:
        try:
            date_obj = datetime.strptime(str(date_str), fmt)
            return date_obj.strftime(output_format)
        except ValueError:
            continue
    
    return date_str  # 変換できない場合は元の値を返す


def format_date_japanese(date_str: str) -> str:
    """日付を日本語フォーマット（YYYY年M月D日）に変換"""
    if not date_str:
        return ""
    
    try:
        # 一旦datetime型に変換
        date_obj = None
        if re.match(r"\d{4}/\d{2}/\d{2}", str(date_str)):
            date_obj = datetime.strptime(str(date_str), "%Y/%m/%d")
        elif re.match(r"\d{4}-\d{2}-\d{2}", str(date_str)):
            date_obj = datetime.strptime(str(date_str), "%Y-%m-%d")
        
        if date_obj:
            # ゼロパディングなしで月日を表示
            return f"{date_obj.year}年{date_obj.month}月{date_obj.day}日"
    except:
        pass
    
    return date_str


def safe_int_convert(value: Union[str, int, float]) -> int:
    """安全に整数に変換"""
    if value is None or value == "":
        return 0
    
    try:
        # 文字列の場合、カンマを除去
        if isinstance(value, str):
            value = value.replace(",", "")
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def convert_room_number(value: any) -> str:
    """部屋番号の変換（小数点除去）"""
    if pd.isna(value) or value is None or value == "":
        return ""
    
    try:
        # 数値の場合は整数に変換してから文字列化
        if isinstance(value, (int, float)):
            return str(int(value))
        
        # 文字列の場合
        str_value = str(value).strip()
        if str_value == "":
            return ""
        
        # 数値文字列で小数点がある場合は整数に変換
        try:
            float_val = float(str_value)
            return str(int(float_val))
        except ValueError:
            # 数値変換できない場合はそのまま返す
            return str_value
    except Exception:
        return str(value) if value is not None else ""


def safe_str_convert(value: any) -> str:
    """安全に文字列に変換（NAN値も空文字に変換）"""
    if value is None:
        return ""
    str_value = str(value).strip()
    # NAN値を空文字に変換
    if str_value.lower() in ['nan', 'none', 'null']:
        return ""
    return str_value


def calculate_exit_fee(rent: Union[str, int], management: Union[str, int], 
                      parking: Union[str, int], other1: Union[str, int]) -> str:
    """退去手続き費用を計算（最低70,000円）"""
    total = (safe_int_convert(rent) + 
             safe_int_convert(management) + 
             safe_int_convert(parking) + 
             safe_int_convert(other1))
    
    return str(max(total, 70000))


def generate_takeover_info(move_in_date: str) -> str:
    """引継情報を生成"""
    formatted_date = format_date(move_in_date)
    return f"●20日～25日頃に督促手数料2,750円or2,970円が加算されることあり。案内注意！！　●入居日：{formatted_date}"


def get_today_formatted() -> str:
    """今日の日付をYYYY/MM/DD形式で取得"""
    return datetime.now().strftime("%Y/%m/%d")


def get_output_filename() -> str:
    """出力ファイル名を生成（MMDDアーク新規登録.csv）"""
    today = datetime.now()
    return f"{today.strftime('%m%d')}アーク新規登録.csv"