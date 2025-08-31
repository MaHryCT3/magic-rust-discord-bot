import calendar
from datetime import datetime, timedelta, timezone
from enum import IntEnum


class WeekDay(IntEnum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class Month(IntEnum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12


def add_timezone(dt: datetime, tz: timezone) -> datetime:
    """Добавляет таймзону не изменяя время"""
    return datetime.combine(dt.date(), dt.time(), tzinfo=tz)


def get_next_monday(dt: datetime | None = None) -> datetime:
    """Возвращает дату следующего понедельника."""
    dt = dt or datetime.now()

    days_until_monday = (7 - dt.weekday()) % 7 or 7
    next_monday = dt + timedelta(days=days_until_monday)
    return next_monday.replace(hour=0, minute=0, second=0, microsecond=0)


def get_next_sunday(dt: datetime | None = None) -> datetime:
    """Возвращает дату следующего воскресенья."""
    dt = dt or datetime.now()

    days_until_sunday = (6 - dt.weekday()) % 7  # 6 — это воскресенье
    next_sunday = dt + timedelta(days=days_until_sunday)
    return next_sunday.replace(hour=0, minute=0, second=0, microsecond=0)


def get_next_month_first_date(dt: datetime | None = None) -> datetime:
    """Возвращает первое число следующего месяца."""
    dt = dt or datetime.now()

    year, month = dt.year, dt.month

    # Если текущий месяц — декабрь, переходим на январь следующего года
    if month == Month.DECEMBER:
        year += 1
        month = 1
    else:
        month += 1

    return datetime(year, month, 1)


def get_last_day_of_month(dt: datetime | None = None) -> datetime:
    """Возвращает последний день месяца для заданной даты."""

    dt = dt or datetime.now()
    # Определяем количество дней в текущем месяце
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    # Возвращаем последний день месяца с временем 23:59:59
    return datetime(dt.year, dt.month, last_day, 23, 59, 59)
