# アークデータインポートツール

アーク新規登録用CSVファイルを自動生成するデータ変換ツールです。

## 概要

2つの元データファイル（案件取込用レポートとContractList）を読み込み、アーク新規登録テンプレート形式のCSVファイルを出力します。

## 機能

- **データ結合**: 利用者番号をキーとした2ファイルの結合
- **フィールドマッピング**: 元データからテンプレート形式への変換
- **データ形式変換**: 日付、電話番号、住所分割等の自動変換
- **固定値設定**: 銀行情報等の固定値自動設定

## ファイル構成

```
ark_import_new_data/
├── main.py              # メイン実行ファイル
├── config.py            # 設定・マッピング定義
├── data_loader.py       # データ読み込み
├── data_transformer.py  # データ変換
├── data_exporter.py     # データ出力
├── requirements.txt     # 依存関係
├── README.md           # このファイル
├── requirements.md      # 要件定義書
├── design.md           # システム設計書
└── tasklist.md         # 実装タスクリスト
```

## 使用方法

### 1. 環境構築
```bash
pip install -r requirements.txt
```

### 2. 実行
```bash
python main.py
```

### 3. 入力ファイル
以下のファイルが必要です：
- `C:/Users/user04/Downloads/【東京支店】①案件取込用レポート20250722.csv`
- `C:/Users/user04/Downloads/ContractList_YYYYMMDDHHMMSS.csv`
- `C:/Users/user04/Desktop/新規登録テンプレ.csv`

### 4. 出力ファイル
- `新規登録アーク_YYYYMMDD.csv` (現在のディレクトリに生成)

## 設定変更

`config.py`でファイルパスやマッピング設定を変更できます。

## 注意事項

- CSVファイルはCP932エンコーディングで処理されます
- ContractListファイルは日時付きファイル名に対応しています
- 処理中にエラーが発生した場合はログを確認してください

## トラブルシューティング

### よくある問題
1. **ファイルが見つからない**: ファイルパスを確認してください
2. **文字化け**: エンコーディングがCP932であることを確認してください
3. **データ不整合**: 元データの利用者番号が一致しているか確認してください

## 開発情報

- **言語**: Python 3.8+
- **主要ライブラリ**: pandas, chardet
- **対応OS**: Windows
- **エンコーディング**: CP932 (Shift_JIS)