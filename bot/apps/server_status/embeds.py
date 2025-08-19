from collections.abc import Iterable

import discord

from core.api_clients.magic_rust import MagicRustServerData
from core.api_clients.magic_rust.models import GAME_MODE_LABELS
from core.localization import LocaleEnum, LocalizationDict, day_name
from core.utils.colors import get_random_blue_color


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
    wipe_label_localization = LocalizationDict(
        {
            LocaleEnum.en: 'Wipe day: ',
            LocaleEnum.ru: 'День вайпа: ',
        }
    )

    def add_server(self, server_data: MagicRustServerData, locale: LocaleEnum = LocaleEnum.ru):
        self.add_field(
            name=f'{server_data.title}',
            value=f'>>> -# {server_data.ip}\n\
            {GAME_MODE_LABELS[server_data.game_mode]}\n\
            {server_data.map}\n\
            {server_data.player_limit.get_label()}\n\
            {server_data.players_online}/{server_data.players_max}\n\
            {self.wipe_label_localization[locale]}{day_name(server_data.wipe_day, locale)}',
        )

    def add_servers(self, servers_data: Iterable[MagicRustServerData], locale: LocaleEnum):
        for server in servers_data:
            self.add_server(server, locale=locale)
