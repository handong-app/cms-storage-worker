from datetime import datetime, timezone, timedelta, time
from zoneinfo import ZoneInfo


def get_seoul_time():
    return datetime.now(ZoneInfo("Asia/Seoul"))

def get_seoul_timestamp():
    return get_seoul_time().timestamp()

def convert_to_kst_datetime(timestamp: float) -> datetime:
    """UTC 타임스탬프를 KST(한국 시간) datetime으로 변환"""
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, tz=timezone.utc) + timedelta(hours=9)

def convert_start_date_to_unix(date_str: str) -> int:
    """yyyy-mm-dd 문자열을 해당 날짜의 시작(00:00:00)의 Unix 타임스탬프로 변환"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    dt_start = datetime.combine(dt.date(), time.min)
    return int(dt_start.timestamp())

def convert_end_date_to_unix(date_str: str) -> int:
    """yyyy-mm-dd 문자열을 해당 날짜의 끝(23:59:59.999999)의 Unix 타임스탬프로 변환"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    dt_end = datetime.combine(dt.date(), time.max)
    return int(dt_end.timestamp())

def convert_unix_to_date_str(ts: int) -> str:
    """Unix 타임스탬프를 "yyyy-mm-dd" 형식의 문자열로 변환"""
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%Y-%m-%d")
