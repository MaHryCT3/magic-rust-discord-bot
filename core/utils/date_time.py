from datetime import datetime, timezone
from enum import IntEnum


class WeekDay(IntEnum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


def add_timezone_info(dt: datetime, tz: timezone) -> datetime:
    """Добавляет таймзону не изменяя время"""
    return datetime.combine(dt.date(), dt.time(), tzinfo=tz)
