# app/core/time.py
from datetime import datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")

def get_kst_now() -> datetime:
    """한국 시간 (KST, UTC+9) 기준 현재 시각 반환"""
    return datetime.now(KST)
