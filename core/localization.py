from enum import StrEnum

from discord.commands.core import valid_locales

from core.utils.date_time import Month, WeekDay


class LocaleEnum(StrEnum):
    """
    Language code
    """

    en = 'en-US'
    ru = 'ru'


DAY_NAMES = {
    LocaleEnum.en: {
        WeekDay.MONDAY: 'Monday',
        WeekDay.TUESDAY: 'Tuesday',
        WeekDay.WEDNESDAY: 'Wednesday',
        WeekDay.THURSDAY: 'Thursday',
        WeekDay.FRIDAY: 'Friday',
        WeekDay.SATURDAY: 'Saturday',
        WeekDay.SUNDAY: 'Sunday',
    },
    LocaleEnum.ru: {
        WeekDay.MONDAY: 'Понедельник',
        WeekDay.TUESDAY: 'Вторник',
        WeekDay.WEDNESDAY: 'Среда',
        WeekDay.THURSDAY: 'Четверг',
        WeekDay.FRIDAY: 'Пятница',
        WeekDay.SATURDAY: 'Суббота',
        WeekDay.SUNDAY: 'Воскресенье',
    },
}

MONTH_NAMES = {
    LocaleEnum.en: {
        Month.JANUARY: 'January',
        Month.FEBRUARY: 'February',
        Month.MARCH: 'March',
        Month.APRIL: 'April',
        Month.MAY: 'May',
        Month.JUNE: 'June',
        Month.JULY: 'July',
        Month.AUGUST: 'August',
        Month.SEPTEMBER: 'September',
        Month.OCTOBER: 'October',
        Month.NOVEMBER: 'November',
        Month.DECEMBER: 'December',
    },
    LocaleEnum.ru: {
        Month.JANUARY: 'Январь',
        Month.FEBRUARY: 'Февраль',
        Month.MARCH: 'Март',
        Month.APRIL: 'Апрель',
        Month.MAY: 'Май',
        Month.JUNE: 'Июнь',
        Month.JULY: 'Июль',
        Month.AUGUST: 'Август',
        Month.SEPTEMBER: 'Сентябрь',
        Month.OCTOBER: 'Октябрь',
        Month.NOVEMBER: 'Ноябрь',
        Month.DECEMBER: 'Декабрь',
    },
}


class LocalizationDict(dict):
    def __init__(
        self,
        localization_map: dict[str, str] = None,
        default_locale: str = LocaleEnum.en,
        **kwargs,
    ) -> None:
        super().__init__(localization_map, **kwargs)
        self.default_locale = default_locale

        for locale in set(valid_locales).difference(self.keys()):
            self[locale] = self[default_locale]


def day_name(day: WeekDay, locale: LocaleEnum) -> str:
    return DAY_NAMES[locale][day]


def month_name(month: Month | int, locale: LocaleEnum) -> str:
    month = Month(month)
    return MONTH_NAMES[locale][month]
