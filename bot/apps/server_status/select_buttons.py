from enum import StrEnum
from typing import TYPE_CHECKING

import discord

from core.api_clients.magic_rust import LIMIT_LABELS, GameModeTypes, Maps
from core.api_clients.magic_rust.models import GAME_MODE_LABELS
from core.localization import LocaleEnum, day_name
from core.utils.date_time import WeekDay

if TYPE_CHECKING:
    from bot.apps.server_status.views import ServerFilterView


class EmptyEnum(StrEnum):
    EMPTY = 'Empty'


class BaseFilterSelect(discord.ui.Select):
    def __init__(self, *args, filter_view: 'ServerFilterView', **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_view = filter_view
        self.availible_options = None

    def on_value_changed(self, value: str | None):
        pass

    @classmethod
    def _get_default_options(cls, locale: LocaleEnum) -> list[discord.SelectOption]:
        pass

    @classmethod
    def _is_option_avalible(cls, option: discord.SelectOption, availible_options: set | None) -> bool:
        return not availible_options or option.value == EmptyEnum.EMPTY or option.value in availible_options

    def set_availible_options(self, availible_options: set | None, default=None):
        self.options = [
            option
            for option in self._get_default_options(self.filter_view.locale)
            if self._is_option_avalible(option, availible_options)
        ]
        if not default:
            return
        for option in self.options:
            if option.value == default:
                option.default = True

    async def callback(self, interaction: discord.Interaction):
        self.on_value_changed(self.values[0] if not self.values[0] == EmptyEnum.EMPTY else None)
        for option in self.options:
            option.default = False
            if option.value == self.values[0] and not self.values[0] == EmptyEnum.EMPTY:
                option.default = True
        await self.filter_view.update(interaction)
        return await super().callback(interaction)


class GameModeSelect(BaseFilterSelect):
    placeholder_localization = {LocaleEnum.ru: 'Режим', LocaleEnum.en: 'Game mode'}

    @classmethod
    def build(cls, filter_view: 'ServerFilterView'):
        return cls(
            filter_view=filter_view,
            placeholder=cls.placeholder_localization[filter_view.locale],
            custom_id='server_filter:select:gm',
            options=cls._get_default_options(filter_view.locale),
        )

    @classmethod
    def _get_default_options(cls, _locale: LocaleEnum):
        options = [discord.SelectOption(label=GAME_MODE_LABELS[gm_type], value=gm_type) for gm_type in GameModeTypes]
        options.insert(0, discord.SelectOption(label='-', value=EmptyEnum.EMPTY))
        return options

    def on_value_changed(self, value: str | None):
        self.filter_view.gm = value


class LimitSelect(BaseFilterSelect):
    placeholder_localization = {LocaleEnum.ru: 'Лимит игроков', LocaleEnum.en: 'Player limit'}

    @classmethod
    def build(cls, filter_view: 'ServerFilterView'):
        return cls(
            filter_view=filter_view,
            placeholder=cls.placeholder_localization[filter_view.locale],
            custom_id='server_filter:select:limit',
            options=cls._get_default_options(filter_view.locale),
        )

    @classmethod
    def _get_default_options(cls, _locale: LocaleEnum):
        options = [discord.SelectOption(label=label, value=str(num)) for num, label in LIMIT_LABELS.items()]
        options.insert(0, discord.SelectOption(label='-', value=EmptyEnum.EMPTY))
        return options

    def on_value_changed(self, value: str | None):
        self.filter_view.limit = int(value) if value else None


class WipeDaySelect(BaseFilterSelect):
    placeholder_localization = {LocaleEnum.ru: 'День вайпа', LocaleEnum.en: 'Wipe day'}

    @classmethod
    def build(cls, filter_view: 'ServerFilterView'):
        return cls(
            filter_view=filter_view,
            placeholder=cls.placeholder_localization[filter_view.locale],
            custom_id='server_filter:select:wipeday',
            options=cls._get_default_options(filter_view.locale),
        )

    @classmethod
    def _get_default_options(cls, locale: LocaleEnum):
        options = [discord.SelectOption(label=day_name(day, locale), value=str(day)) for day in WeekDay]
        options.insert(0, discord.SelectOption(label='-', value=EmptyEnum.EMPTY))
        return options

    def on_value_changed(self, value: str | None):
        self.filter_view.wipeday = int(value) if value else None


class MapSelect(BaseFilterSelect):
    placeholder_localization = {LocaleEnum.ru: 'Карта', LocaleEnum.en: 'Map'}

    @classmethod
    def build(cls, filter_view: 'ServerFilterView'):
        return cls(
            filter_view=filter_view,
            placeholder=cls.placeholder_localization[filter_view.locale],
            custom_id='server_filter:select:map',
            options=cls._get_default_options(filter_view.locale),
        )

    @classmethod
    def _get_default_options(cls, _locale: LocaleEnum):
        maps_options = [discord.SelectOption(label=map) for map in Maps]
        options = [discord.SelectOption(label='-', value=EmptyEnum.EMPTY), *maps_options]
        return options

    def on_value_changed(self, value: str | None):
        self.filter_view.map_type = value
