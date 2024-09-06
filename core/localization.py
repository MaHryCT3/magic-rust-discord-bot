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
