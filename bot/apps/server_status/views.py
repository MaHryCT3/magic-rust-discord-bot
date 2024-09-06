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
from core.clients.server_data_api import MagicRustServerDataAPI
from core.clients.server_data_api.models import FullServerData
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
    def __init__(self, locale: LocaleEnum):
        self.locale = locale
        gm_select = GameModeSelect.build(self)
        limit_select = LimitSelect.build(self)
        wipeday_select = WipeDaySelect.build(self)
        map_select = MapSelect.build(self)
        super().__init__(gm_select, limit_select, wipeday_select, map_select, timeout=None)
        self.gm: str | None = None
        self.limit: int | None = None
        self.wipeday: int | None = None
        self.map: str | None = None

    async def update(self, interaction: discord.Interaction):
        servers_data: list[FullServerData] = await MagicRustServerDataAPI().get_combined_servers_data()
        servers_data.sort(key=lambda item: item.num)
        server_info_embed = ServerInfoEmbed()
        for server_data in servers_data:
            if self._is_server_satisfying_filter(server_data):
                server_info_embed.add_server(server_data, self.locale)
        if not server_info_embed.fields:
            await interaction.response.edit_message(embeds=[], files=[], attachments=[], view=self)
            return
        await interaction.response.edit_message(embed=server_info_embed, files=[], attachments=[], view=self)

    def _is_server_satisfying_filter(self, server_data: FullServerData) -> bool:
        return (
            (not self.gm or server_data.gm.value == self.gm)
            and (not self.limit or server_data.limit == self.limit)
            and (not self.wipeday or server_data.wipeday == self.wipeday)
            and (not self.map or server_data.map.value == self.map)
        )
