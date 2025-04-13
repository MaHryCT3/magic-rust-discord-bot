import datetime

import discord

from bot.constants import MAIN_COLOR
from core.localization import LocaleEnum
from core.utils.format_strings import format_default_time, format_link_text


class TicketHeaderEmbed(discord.Embed):
    created_at_localization = {
        LocaleEnum.ru: '⏱️Время открытия',
        LocaleEnum.en: '⏱️Open Time',
    }

    opened_by_localization = {
        LocaleEnum.ru: '✅Открыто',
        LocaleEnum.en: '✅Opened By',
    }

    description_localization = {
        LocaleEnum.ru: 'Описание обращения',
        LocaleEnum.en: 'Ticket description',
    }

    closed_by_localization = {
        LocaleEnum.ru: '🔒Закрыто',
        LocaleEnum.en: '🔒Closed by',
    }

    closed_at_localization = {
        LocaleEnum.ru: '⏰Время закрытия',
        LocaleEnum.en: '⏰Close Time',
    }

    transcript_localization = {
        LocaleEnum.ru: '📜История',
        LocaleEnum.en: '📜History',
    }

    @classmethod
    def build(
        cls,
        locale: LocaleEnum,
        ticket_number: int,
        created_at: datetime.datetime,
        user_steam: str,
        description: str,
        opened_by: discord.Member | None = None,
        closed_by: discord.Member | None = None,
        closed_at: datetime.datetime | None = None,
        transcript_url: str | None = None,
    ):
        embed = cls(color=MAIN_COLOR)
        embed.fields = []
        embed.add_field(
            name='#️⃣Ticket ID',
            value=str(ticket_number),
        )
        embed.add_field(
            name=cls.opened_by_localization[locale],
            value=opened_by.mention if opened_by else 'Member not found',
        )
        embed.add_field(
            name=cls.created_at_localization[locale],
            value=format_default_time(created_at),
        )
        embed.add_field(
            name='Steam',
            value=user_steam,
            inline=False,
        )
        embed.add_field(
            name=cls.description_localization[locale],
            value=description,
            inline=False,
        )
        if transcript_url:
            embed.add_field(
                name='',
                value=format_link_text(
                    text=cls.transcript_localization[locale],
                    link=transcript_url,
                ),
                inline=False,
            )
        if closed_by:
            embed.add_field(
                name=cls.closed_by_localization[locale],
                value=closed_by.mention,
            )
        if closed_at:
            embed.add_field(
                name=cls.closed_at_localization[locale],
                value=format_default_time(closed_at),
            )
        return embed
