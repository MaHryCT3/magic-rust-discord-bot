import discord

from bot.constants import MAIN_COLOR
from core.localization import LocaleEnum, LocalizationDict


class ControlPanelImageEmbed(discord.Embed):
    image_localization = {
        LocaleEnum.en: 'https://i.imgur.com/ApQ9szo.jpeg',
        LocaleEnum.ru: 'https://i.imgur.com/cSCDDBP.jpeg',
    }

    @classmethod
    def build(
        cls,
        locale: LocaleEnum,
    ):
        embed = cls(color=MAIN_COLOR)
        embed.set_image(url=cls.image_localization[locale])
        return embed


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


class InsufficientPermissionsEmbed(discord.Embed):
    title_localization = LocalizationDict(
        {
            LocaleEnum.en: 'Insufficient permissions!',
            LocaleEnum.ru: 'Недостаточно прав!',
        }
    )
    description_localization = LocalizationDict(
        {
            LocaleEnum.en: 'Only channel creator can manage it.',
            LocaleEnum.ru: 'Только создатель канала может им управлять.',
        }
    )

    @classmethod
    def build(
        cls,
        locale: LocaleEnum,
    ):
        embed = cls()
        embed.title = cls.title_localization[locale]
        embed.add_field(name='', value=cls.description_localization[locale], inline=False)
        return embed


class KickEmbed(discord.Embed):
    title_localization = LocalizationDict(
        {
            LocaleEnum.en: 'Kick channel member',
            LocaleEnum.ru: 'Выгнать участника канала',
        }
    )
    description_localization = LocalizationDict(
        {
            LocaleEnum.en: "Choose a member from the list below. He won't be able to connect to this channel again.",
            LocaleEnum.ru: 'Выберите участника из списка ниже. Он больше не сможет зайти в этот канал снова.',
        }
    )

    @classmethod
    def build(
        cls,
        locale: LocaleEnum,
    ):
        embed = cls()
        embed.title = cls.title_localization[locale]
        embed.add_field(name='', value=cls.description_localization[locale], inline=False)
        return embed
