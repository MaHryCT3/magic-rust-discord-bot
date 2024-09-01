from datetime import datetime, timezone

DAY_NAMES = {
    1: 'Monday',
    2: 'Tuesday',
    3: 'Wednesday',
    4: 'Thursday',
    5: 'Friday',
    6: 'Saturday',
    7: 'Sunday',
}

def add_timezone_info(dt: datetime, tz: timezone) -> datetime:
    """Добавляет таймзону не изменяя время"""
    return datetime.combine(dt.date(), dt.time(), tzinfo=tz)

def day_num_to_name(num: int):
    return DAY_NAMES[num]