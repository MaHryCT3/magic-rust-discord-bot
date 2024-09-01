import discord

from core.clients.server_data_api import LIMIT_LABELS, ServerData
from core.localization import LocaleEnum, LocalizationDict
from core.utils.colors import get_random_blue_color
from core.utils.date_time import day_num_to_name
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
        self.add_field(name=f'MAGIC RUST #{server_data.num}', value=f'>>> -# {server_data.ip}\n\
            {server_data.gm}\n\
            {server_data.map}\n\
            {LIMIT_LABELS[server_data.limit]}\n\
            {server_data.players}/{server_data.maxplayers}\n\
            {day_num_to_name(server_data.wipeday)}')