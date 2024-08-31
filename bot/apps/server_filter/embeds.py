import discord

from core.clients.server_data_api import ServerData
from core.localization import LocaleEnum, LocalizationDict
from core.utils.colors import get_random_blue_color
from core.utils.format_strings import bold_message


class ServerFilterGreetingEmbed(discord.Embed):
    title_localization = LocalizationDict(
        {
            LocaleEnum.en: 'You can find the server you need here!',
            LocaleEnum.ru: 'Здесь можно найти подходящий сервер!',
        }
    )


    @classmethod
    def build(
        cls,
        locale: LocaleEnum = LocaleEnum.en,
    ):
        embed = cls(color=get_random_blue_color())
        embed.title = cls.title_localization[locale]
        return embed

class ServerInfoEmbed(discord.Embed):
    def add_server(self, server_data: ServerData):
        self.add_field(name=f'MAGIC RUST #{server_data.num}', value=f'asda')
        self.add_field(name="Gamemode", value=server_data.gm, inline=True)