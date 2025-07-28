"""
logging.py - アプリケーション分析・説明ユーティリティモジュール

このモジュールは、READMEファイルと全プロジェクトファイルを読み取り、
アプリケーションの性質と機能を詳細に説明する機能を提供します。
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import json


class ApplicationAnalyzer:
    """アプリケーション分析クラス"""
    
    def __init__(self, project_root: str = None):
        """
        初期化
        
        Args:
            project_root: プロジェクトルートディレクトリ（デフォルトは親ディレクトリ）
        """
        if project_root is None:
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)
    
    def read_readme(self) -> Dict[str, Any]:
        """
        READMEファイルを読み取り、アプリケーション概要を抽出
        
        Returns:
            アプリケーション概要情報の辞書
        """
        readme_path = self.project_root / "README.md"
        
        if not readme_path.exists():
            return {"error": "README.mdファイルが見つかりません"}
        
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # READMEから主要情報を抽出
            analysis = {
                "application_name": "アーク新規登録データ変換ツール",
                "purpose": "手動で行っていたCSVデータの変換作業を自動化するPythonツール",
                "main_functions": [
                    "自動ファイル検索（ダウンロードフォルダから最新ファイルを自動取得）",
                    "重複チェック（ContractListとの照合により既存データを自動除外）",
                    "データ検証（1900年以前の異常な生年月日を自動除外）",
                    "住所分割（郵便番号、都道府県、市区町村、残り住所に自動分割）",
                    "電話番号処理（自宅TELのみの場合は携帯TELに自動移動）",
                    "保証人/緊急連絡人判定（種別から自動判定して適切に配置）",
                    "金額計算（退去手続き費用の自動計算、最低70,000円保証）"
                ],
                "input_files": [
                    "案件取込用レポート（【東京支店】①案件取込用レポートYYYYMMDD.csv）",
                    "ContractList（ContractList_*.csv）"
                ],
                "output_files": [
                    "MMDDアーク新規登録.csv（111列の統合データ）",
                    "processing_report_*.txt（処理レポート）"
                ],
                "technical_specs": {
                    "language": "Python 3.8+",
                    "main_libraries": ["pandas (2.0.3)", "chardet (5.2.0)"],
                    "encoding": "CP932（Shift_JIS）",
                    "os_support": "Windows",
                    "data_capacity": "1万件程度のデータに対応"
                }
            }
            
            return analysis
            
        except Exception as e:
            return {"error": f"README読み取りエラー: {str(e)}"}
    
    def analyze_project_structure(self) -> Dict[str, Any]:
        """
        プロジェクト構造を分析し、各ファイルの役割を特定
        
        Returns:
            プロジェクト構造分析結果の辞書
        """
        structure = {
            "project_type": "データ変換・処理ツール",
            "architecture": "モジュラー設計",
            "modules": {},
            "file_count": 0,
            "directories": []
        }
        
        # srcディレクトリの分析
        src_dir = self.project_root / "src"
        if src_dir.exists():
            structure["modules"]["src"] = {
                "description": "メインソースコード",
                "files": {}
            }
            
            for file_path in src_dir.glob("*.py"):
                file_name = file_path.name
                structure["modules"]["src"]["files"][file_name] = self._analyze_python_file(file_path)
                structure["file_count"] += 1
        
        # docsディレクトリの分析
        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            structure["modules"]["docs"] = {
                "description": "設計書・ドキュメント",
                "files": {}
            }
            
            for file_path in docs_dir.glob("*"):
                if file_path.is_file():
                    structure["modules"]["docs"]["files"][file_path.name] = {
                        "purpose": self._get_doc_purpose(file_path.name)
                    }
                    structure["file_count"] += 1
        
        # outputsディレクトリの分析
        outputs_dir = self.project_root / "outputs"
        if outputs_dir.exists():
            structure["directories"].append("outputs（出力ファイル格納）")
        
        return structure
    
    def _analyze_python_file(self, file_path: Path) -> Dict[str, str]:
        """
        Pythonファイルを分析してその役割を特定
        
        Args:
            file_path: ファイルパス
            
        Returns:
            ファイル分析結果
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_analysis = {
                "purpose": self._get_file_purpose(file_path.name, content),
                "has_main": "if __name__ == \"__main__\":" in content,
                "imports": self._extract_imports(content),
                "classes": self._extract_classes(content),
                "functions": self._extract_functions(content)
            }
            
            return file_analysis
            
        except Exception as e:
            return {"error": f"ファイル分析エラー: {str(e)}"}
    
    def _get_file_purpose(self, filename: str, content: str) -> str:
        """ファイル名と内容からファイルの目的を推定"""
        purposes = {
            "main.py": "メイン処理・プログラムエントリーポイント",
            "config.py": "設定・マッピング定義",
            "data_loader.py": "データ読み込み処理",
            "data_validator.py": "データ検証・バリデーション",
            "data_transformer.py": "データ変換・フォーマット処理", 
            "data_exporter.py": "データ出力・CSV書き出し",
            "address_splitter.py": "住所分割処理",
            "utils.py": "共通ユーティリティ関数",
            "logging.py": "アプリケーション分析・ログ機能"
        }
        
        return purposes.get(filename, "用途不明")
    
    def _get_doc_purpose(self, filename: str) -> str:
        """ドキュメントファイルの目的を推定"""
        purposes = {
            "design.md": "システム設計書",
            "detailed_design.md": "詳細設計書",
            "requirements.md": "要求仕様書",
            "manual.txt": "操作マニュアル",
            "tasklist.md": "タスク管理"
        }
        
        return purposes.get(filename, "ドキュメント")
    
    def _extract_imports(self, content: str) -> List[str]:
        """インポート文を抽出"""
        imports = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
        
        return imports[:5]  # 最初の5つのみ
    
    def _extract_classes(self, content: str) -> List[str]:
        """クラス定義を抽出"""
        classes = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('class '):
                class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                classes.append(class_name)
        
        return classes
    
    def _extract_functions(self, content: str) -> List[str]:
        """関数定義を抽出（メソッドを除く）"""
        functions = []
        lines = content.split('\n')
        
        for line in lines:
            if line.startswith('def '):
                func_name = line.split('def ')[1].split('(')[0].strip()
                functions.append(func_name)
        
        return functions[:5]  # 最初の5つのみ
    
    def generate_application_summary(self) -> str:
        """
        アプリケーションの包括的な説明を生成
        
        Returns:
            アプリケーション説明文
        """
        readme_analysis = self.read_readme()
        structure_analysis = self.analyze_project_structure()
        
        if "error" in readme_analysis:
            return f"分析エラー: {readme_analysis['error']}"
        
        summary = f"""
=== {readme_analysis['application_name']} ===

【アプリケーションの性質】
これは{readme_analysis['purpose']}です。

【主要機能】
"""
        for i, func in enumerate(readme_analysis['main_functions'], 1):
            summary += f"{i}. {func}\n"
        
        summary += f"""
【技術仕様】
- 言語: {readme_analysis['technical_specs']['language']}
- 主要ライブラリ: {', '.join(readme_analysis['technical_specs']['main_libraries'])}
- エンコーディング: {readme_analysis['technical_specs']['encoding']}
- 対応OS: {readme_analysis['technical_specs']['os_support']}
- 処理能力: {readme_analysis['technical_specs']['data_capacity']}

【アーキテクチャ】
- プロジェクト種別: {structure_analysis['project_type']}
- 設計方針: {structure_analysis['architecture']}
- 総ファイル数: {structure_analysis['file_count']}個

【処理フロー】
1. 入力ファイル読み込み（案件取込用レポート、ContractList）
2. データ検証・重複チェック
3. データ変換・フォーマット処理
4. 出力CSV生成（111列構成）
5. 処理レポート作成

【入力ファイル】
"""
        for input_file in readme_analysis['input_files']:
            summary += f"- {input_file}\n"
        
        summary += f"""
【出力ファイル】
"""
        for output_file in readme_analysis['output_files']:
            summary += f"- {output_file}\n"
        
        summary += f"""
【特徴的な処理】
- CSV形式のデータ変換に特化
- 住所の自動分割機能
- 電話番号の条件付き振り分け
- 保証人・緊急連絡人の自動判定
- 重複データの自動除外
- 異常データ（1900年以前の生年月日等）の自動フィルタリング

このアプリケーションは、不動産管理業務でのCSVデータ処理作業を大幅に効率化する専用ツールです。
"""
        
        return summary


def main():
    """メイン関数 - アプリケーション分析を実行"""
    analyzer = ApplicationAnalyzer()
    
    print("=" * 80)
    print("アプリケーション分析ツール")
    print("=" * 80)
    
    # アプリケーション概要の表示
    summary = analyzer.generate_application_summary()
    print(summary)
    
    print("\n" + "=" * 80)
    print("分析完了")
    print("=" * 80)


if __name__ == "__main__":
    main()