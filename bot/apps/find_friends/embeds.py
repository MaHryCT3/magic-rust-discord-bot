import discord

from core.localization import LocaleEnum, LocalizationDict
from core.utils.colors import get_random_blue_color
from core.utils.format_strings import bold_message


class FindFriendEmbed(discord.Embed):
    servers_label = LocalizationDict(
        {
            LocaleEnum.en: 'Server(s)',
            LocaleEnum.ru: 'Сервер(а)',
        }
    )

    @classmethod
    def build(
        cls,
        author_name: str,
        author_icon_url: str,
        article: str,
        message: str,
        servers: str,
        locale: LocaleEnum,
    ):
        embed = cls(color=get_random_blue_color())
        embed.set_author(name=author_name, icon_url=author_icon_url)
        embed.title = article
        embed.add_field(name='', value=message, inline=False)
        embed.add_field(name='', value=bold_message(cls.servers_label[locale]), inline=True)
        embed.add_field(name='', value=servers, inline=False)
        return embed
