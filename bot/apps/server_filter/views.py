from typing import Self
import discord

from bot.apps.server_filter.embeds import ServerInfoEmbed
from core.clients.server_data_api import get_servers_data_async
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
        await interaction.response.send_message("You clicked the button!", view=ServerFilterView(locale=LocaleEnum.en), ephemeral=True) #TODO: send view


class ServerFilterView(discord.ui.View):
    def __init__(self, locale):
        self.locale = locale
        gm_select = discord.ui.Select(custom_id=f'server_filter:{locale}:select:gm',
                                   options=[discord.SelectOption(label='vanilla'), discord.SelectOption(label='vanillax2'), discord.SelectOption(label='modded')])
        gm_select.callback = self._select_callback
        super().__init__(gm_select, timeout=None)

    @classmethod
    async def _select_callback(cls, interaction: discord.Interaction):
        servers_data = await get_servers_data_async()
        server_info_embed = ServerInfoEmbed()
        for server_data in servers_data:
            server_info_embed.add_server(server_data)
        await interaction.response.edit_message(content="sdfsd", embed=server_info_embed, files=[], attachments=[])
        