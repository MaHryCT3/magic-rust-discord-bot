from datetime import datetime, timezone


def add_timezone_info(dt: datetime, tz: timezone) -> datetime:
    """Добавляет таймзону не изменяя время"""
    return datetime.combine(dt.date(), dt.time(), tzinfo=tz)
