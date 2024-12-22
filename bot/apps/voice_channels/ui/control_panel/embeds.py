import discord

from bot.constants import MAIN_COLOR
from core.localization import LocaleEnum


class InsufficientPermissionsEmbed(discord.Embed):
    title_localization = {
        LocaleEnum.en: 'Insufficient permissions!',
        LocaleEnum.ru: 'Недостаточно прав!',
    }
    description_localization = {
        LocaleEnum.en: 'Only channel creator can manage it.',
        LocaleEnum.ru: 'Только создатель канала может им управлять.',
    }

    @classmethod
    def build(
        cls,
        locale: LocaleEnum,
    ):
        embed = cls()
        embed.title = cls.title_localization[locale]
        embed.add_field(name='', value=cls.description_localization[locale], inline=False)
        return embed


class ControlPanelImageEmbed(discord.Embed):
    image_localization = {
        LocaleEnum.en: 'https://i.imgur.com/MACUJao.png',
        LocaleEnum.ru: 'https://i.imgur.com/9HBlp3F.png',
    }

    @classmethod
    def build(
        cls,
        locale: LocaleEnum,
    ):
        embed = cls(color=MAIN_COLOR)
        embed.set_image(url=cls.image_localization[locale])
        return embed


# NOTE: Более не используется
class ControlPanelTextEmbed(discord.Embed):
    title_localization = {
        LocaleEnum.ru: 'Вы можете настроить канал, используя обычные настройки дискорда. '
        'Указать лимит, переименовать канал и так далее',
        LocaleEnum.en: 'You can customize the channel using the default discord settings. '
        'Specify a limit, rename the channel, etc.',
    }

    @classmethod
    def build(
        cls,
        locale: LocaleEnum,
    ):
        embed = cls(color=MAIN_COLOR, title=cls.title_localization[locale])
        return embed
