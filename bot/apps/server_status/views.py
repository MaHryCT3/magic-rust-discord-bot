import itertools
from enum import StrEnum
from typing import Self

import discord

from bot.apps.server_status import buttons
from bot.apps.server_status.embeds import ServerInfoEmbed
from bot.apps.server_status.select_buttons import (
    GameModeSelect,
    LimitSelect,
    MapSelect,
    WipeDaySelect,
)
from core.api_clients.magic_rust import FullServerData, MagicRustServerDataAPI
from core.localization import LocaleEnum


class FindServerView(discord.ui.View):
    def __init__(self, locale: LocaleEnum):
        self.locale = locale
        button = buttons.FindServerButton(locale)
        super().__init__(button, timeout=None)

    @classmethod
    def get_localized_views(cls: Self) -> dict[LocaleEnum, Self]:
        localized_views: dict[LocaleEnum, cls] = {}
        for locale in buttons.FindServerButton.label_localization.keys():
            localized_views[locale] = cls(locale)
        return localized_views


class ServerFilterView(discord.ui.View):
    class FilterFields(StrEnum):
        GM = 'gm'
        LIMIT = 'limit'
        WIPEDAY = 'wipeday'
        MAP = 'map'

    def __init__(self, locale: LocaleEnum):
        self.locale = locale
        self.gm_select = GameModeSelect.build(self)
        self.limit_select = LimitSelect.build(self)
        self.wipeday_select = WipeDaySelect.build(self)
        self.map_select = MapSelect.build(self)
        super().__init__(self.gm_select, self.limit_select, self.wipeday_select, self.map_select, timeout=None)
        self.gm: str | None = None
        self.limit: int | None = None
        self.wipeday: int | None = None
        self.map: str | None = None

    async def update(self, interaction: discord.Interaction):
        servers_data = await MagicRustServerDataAPI().get_combined_servers_data()
        servers_data.sort(key=lambda item: item.num)
        filtered_servers_data = [
            server_data for server_data in servers_data if self._is_server_satisfying_filter(server_data)
        ]

        if not filtered_servers_data:
            await interaction.response.edit_message(embeds=[], files=[], attachments=[], view=self)
            return

        embeds = []
        # 25 ограничение полей в ембедах
        for server_datas in itertools.batched(filtered_servers_data, 25):
            embed = ServerInfoEmbed()
            embed.add_servers(server_datas, locale=self.locale)
            embeds.append(embed)

        self.availible_gms = {
            server_data.gm
            for server_data in servers_data
            if self._is_server_satisfying_filter(server_data, exclude=self.FilterFields.GM)
        }

        self.availible_limits = {
            str(server_data.limit)
            for server_data in servers_data
            if self._is_server_satisfying_filter(server_data, exclude=self.FilterFields.LIMIT)
        }
        self.availible_wipedays = {
            str(server_data.wipeday)
            for server_data in servers_data
            if self._is_server_satisfying_filter(server_data, exclude=self.FilterFields.WIPEDAY)
        }
        self.availible_maps = {
            server_data.map
            for server_data in servers_data
            if self._is_server_satisfying_filter(server_data, exclude=self.FilterFields.MAP)
        }
        self._set_availible_selects()
        await interaction.response.edit_message(embeds=embeds, files=[], attachments=[], view=self)

    def _is_server_satisfying_filter(self, server_data: FullServerData, exclude: FilterFields | None = None) -> bool:
        return (
            (self.gm in (None, server_data.gm) or exclude == self.FilterFields.GM)
            and (self.limit in (None, server_data.limit) or exclude == self.FilterFields.LIMIT)
            and (self.wipeday in (None, server_data.wipeday) or exclude == self.FilterFields.WIPEDAY)
            and (self.map in (None, server_data.map) or exclude == self.FilterFields.MAP)
        )

    def _set_availible_selects(self):
        self.clear_items()
        if len(self.availible_gms) > 1 or self.gm is not None:
            self.gm_select.set_availible_options(self.availible_gms, default=self.gm)
            self.add_item(self.gm_select)
        if len(self.availible_limits) > 1 or self.limit is not None:
            self.limit_select.set_availible_options(self.availible_limits, default=str(self.limit))
            self.add_item(self.limit_select)
        if len(self.availible_wipedays) > 1 or self.wipeday is not None:
            self.wipeday_select.set_availible_options(self.availible_wipedays, default=str(self.wipeday))
            self.add_item(self.wipeday_select)
        if len(self.availible_maps) > 1 or self.map is not None:
            self.map_select.set_availible_options(self.availible_maps, default=self.map)
            self.add_item(self.map_select)
