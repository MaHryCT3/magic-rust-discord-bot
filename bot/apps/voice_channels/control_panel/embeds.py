import discord

from core.localization import LocaleEnum, LocalizationDict
from core.utils.format_strings import bold_message


class ControlPanelEmbed(discord.Embed):
    title_localization = LocalizationDict(
        {
            LocaleEnum.en: 'Channel control panel',
            LocaleEnum.ru: 'Панель управления каналом',
        }
    )
    kick_localization = LocalizationDict(
        {
            LocaleEnum.en: ':dizzy_face: Kick',
            LocaleEnum.ru: ':dizzy_face: Выгнать',
        }
    )
    kick_description_localization = LocalizationDict(
        {
            LocaleEnum.en: f'Kick channel member {bold_message("permanently")}',
            LocaleEnum.ru: f'Выгнать участника канала {bold_message("навсегда")}',
        }
    )

    @classmethod
    def build(
        cls,
        locale: LocaleEnum,
    ):
        embed = cls()
        embed.title = cls.title_localization[locale]
        embed.add_field(
            name=cls.kick_localization[locale], value=cls.kick_description_localization[locale], inline=False
        )
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
