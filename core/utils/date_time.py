from datetime import datetime, timezone

from core.localization import LocaleEnum

DAY_NAMES = {
    LocaleEnum.en: {
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
        7: 'Sunday',
    },
    LocaleEnum.ru: {
        1: 'Понедельник',
        2: 'Вторник',
        3: 'Среда',
        4: 'Четверг',
        5: 'Пятница',
        6: 'Суббота',
        7: 'Воскресенье',
    },
}


def add_timezone_info(dt: datetime, tz: timezone) -> datetime:
    """Добавляет таймзону не изменяя время"""
    return datetime.combine(dt.date(), dt.time(), tzinfo=tz)


def day_num_to_name(num: int, locale: LocaleEnum):
    return DAY_NAMES[locale][num]
