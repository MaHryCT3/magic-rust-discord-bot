from typing import Self
import discord

from bot.apps.server_filter.buttons import GameModeSelect, LimitSelect, MapSelect, WipeDaySelect
from bot.apps.server_filter.embeds import ServerInfoEmbed
from core.clients.server_data_api import ServerData, get_servers_data_async
from core.localization import LocaleEnum, LocalizationDict



class ServerFilterGreetingView(discord.ui.View):
    send_filter_button_localization = LocalizationDict(
    {
        LocaleEnum.en: 'Find server',
        LocaleEnum.ru: 'Подобрать сервер',
    }
    )
    def __init__(self, locale):
        self.locale = locale
        button = discord.ui.Button(style=discord.ButtonStyle.primary,
                                   custom_id=f'server_filter:{locale}:button:send_filter',
                                   label=self.send_filter_button_localization[locale])
        button.callback = self._button_callback
        super().__init__(button, timeout=None)

    @classmethod
    async def get_localization_views(cls: Self) -> dict[LocaleEnum, 'ServerFilterGreetingView']:
        localization_views: dict[LocaleEnum, cls] = {}
        for locale in cls.send_filter_button_localization.keys():
            localization_views[locale] = cls(locale)
        return localization_views

    @classmethod
    async def _button_callback(cls, interaction: discord.Interaction):
        await interaction.response.send_message(view=ServerFilterView(locale=LocaleEnum.en), ephemeral=True) #TODO: send view


class ServerFilterView(discord.ui.View):
    gm: str | None = None
    limit: int | None = None
    wipeday: int | None = None
    map: str | None = None

    def __init__(self, locale):
        self.locale = locale
        gm_select = GameModeSelect.build(self)
        limit_select = LimitSelect.build(self)
        wipeday_select = WipeDaySelect.build(self)
        map_select = MapSelect.build(self)
        super().__init__(gm_select, limit_select, wipeday_select, map_select, timeout=None)
    
    async def update(self, interaction: discord.Interaction):
        servers_data: list[ServerData] = await get_servers_data_async()
        server_info_embed = ServerInfoEmbed()
        for server_data in servers_data:
            if (not self.gm or server_data.gm == self.gm) and \
            (not self.limit or server_data.limit == self.limit) and \
            (not self.wipeday or server_data.wipeday == self.wipeday) and \
            (not self.map or server_data.map == self.map):
                server_info_embed.add_server(server_data)
        if not server_info_embed.fields:
            await interaction.response.edit_message(embeds=[], files=[], attachments=[], view=self)
            return
        await interaction.response.edit_message(embed=server_info_embed, files=[], attachments=[], view=self)