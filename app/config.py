import os
from typing import List


def _csv_to_list(raw: str, cast=str) -> List:
    values = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            values.append(cast(chunk))
        except (TypeError, ValueError):
            continue
    return values


class Config:
    """Default application configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Session / security
    SESSION_PERMANENT = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "1") == "1"
    WTF_CSRF_TIME_LIMIT = None

    # Database
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    DB_PATH = os.environ.get("DB_PATH", "production_log_v3.db")
    SQL_ECHO = os.environ.get("SQL_ECHO", "0") == "1"

    # Domain settings
    SHIFT_CHOICES = _csv_to_list(os.environ.get("SHIFT_CHOICES", "A,B,C"))
    MACHINE_CHOICES = _csv_to_list(os.environ.get("MACHINE_CHOICES", "2,3,4,5,6"), int)
    MODEL_CHOICES = _csv_to_list(
        os.environ.get(
            "MODEL_CHOICES",
            "sample1,sample2,sample3,sample4,sample5,sample6,sample7,sample8,sample9,sample10",
        )
    )
    RECORDS_LIMIT = int(os.environ.get("RECORDS_LIMIT", "250"))
    EXPORT_FILENAME = os.environ.get("EXPORT_FILENAME", "production-log-export.csv")

    PATCH_NOTES = [
        {
            "version": "3.0.1",
            "date": "2025-11-15",
            "items": [
                "ヘッダーからトップページに遷移できるよう改善",
                "パッチノート／使い方／フィードバック導線を追加",
            ],
        },
        {
            "version": "3.0.0",
            "date": "2025-11-10",
            "items": [
                "UI 全面刷新とフォームの必須バリデーションを強化",
                "CSV 出力やフィルタリングの導線を整理",
            ],
        },
    ]

    USAGE_GUIDE = [
        {
            "title": "1. 号機を選ぶ",
            "details": "QR か 号機選択画面から入力対象の号機を指定します。",
        },
        {
            "title": "2. 実測値を入力",
            "details": "入力フォームで勤務帯やモニタ値を登録し、保存ボタンで記録します。",
        },
        {
            "title": "3. 一覧・CSV",
            "details": "一覧画面と CSV を活用して過去データを確認・共有できます。",
        },
    ]

    FEEDBACK_CATEGORIES = [
        ("idea", "機能追加の要望"),
        ("ux", "使いやすさ / UI"),
        ("bug", "不具合・トラブル"),
        ("other", "その他"),
    ]
