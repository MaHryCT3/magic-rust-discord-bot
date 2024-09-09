from enum import StrEnum

from discord.commands.core import valid_locales

from core.utils.date_time import WeekDay


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
