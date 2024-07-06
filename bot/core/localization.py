from enum import StrEnum

from discord.commands.core import valid_locales


class LocaleEnum(StrEnum):
    en = 'en-US'
    ru = 'ru'


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
