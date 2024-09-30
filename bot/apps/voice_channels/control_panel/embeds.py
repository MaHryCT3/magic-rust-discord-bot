import discord

from bot.constants import MAIN_COLOR
from core.localization import LocaleEnum, LocalizationDict


class ControlPanelEmbed(discord.Embed):
    title_localization = LocalizationDict(
        {
            LocaleEnum.en: 'Channel control panel',
            LocaleEnum.ru: 'Панель управления каналом',
        }
    )

    @classmethod
    def build(
        cls,
        locale: LocaleEnum,
    ):
        embed = cls(color=MAIN_COLOR)
        embed.title = cls.title_localization[locale]
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
