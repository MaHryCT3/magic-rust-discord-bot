from enum import StrEnum
from typing import TYPE_CHECKING

import discord

from core.clients.server_data_api.models import LIMIT_LABELS, GameModeTypes, Maps
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

    def on_value_changed(self, value: str | None):
        pass

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
        options = [discord.SelectOption(label=gm_type) for gm_type in GameModeTypes]
        options.insert(0, discord.SelectOption(label='-', value=EmptyEnum.EMPTY))
        return cls(
            filter_view=filter_view,
            placeholder=cls.placeholder_localization[filter_view.locale],
            custom_id='server_filter:select:gm',
            options=options,
        )

    def on_value_changed(self, value: str | None):
        self.filter_view.gm = value


class LimitSelect(BaseFilterSelect):
    placeholder_localization = {LocaleEnum.ru: 'Лимит игроков', LocaleEnum.en: 'Player limit'}

    @classmethod
    def build(cls, filter_view: 'ServerFilterView'):
        options = [discord.SelectOption(label=label, value=str(num)) for num, label in LIMIT_LABELS.items()]
        options.insert(0, discord.SelectOption(label='-', value=EmptyEnum.EMPTY))
        return cls(
            filter_view=filter_view,
            placeholder=cls.placeholder_localization[filter_view.locale],
            custom_id='server_filter:select:limit',
            options=options,
        )

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
            options=[
                discord.SelectOption(label='-', value=EmptyEnum.EMPTY),
                discord.SelectOption(label=day_name(WeekDay.MONDAY, filter_view.locale), value=str(WeekDay.MONDAY)),
                discord.SelectOption(label=day_name(WeekDay.THURSDAY, filter_view.locale), value=str(WeekDay.THURSDAY)),
                discord.SelectOption(label=day_name(WeekDay.FRIDAY, filter_view.locale), value=str(WeekDay.FRIDAY)),
            ],
        )

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
            options=[
                discord.SelectOption(label='-', value=EmptyEnum.EMPTY),
                discord.SelectOption(label=Maps.PRECEDURAL_PLUS),
                discord.SelectOption(label=Maps.BARREN_PLUS),
            ],
        )

    def on_value_changed(self, value: str | None):
        self.filter_view.map = value
