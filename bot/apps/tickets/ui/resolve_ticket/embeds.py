import datetime
from typing import Self

import discord

from bot.apps.tickets.constants import HOURS_TO_CLOSE_TICKET_MARK_AS_RESOLVED
from bot.config import settings
from bot.constants import MAIN_COLOR
from core.localization import LocaleEnum
from core.utils.format_strings import mention_user


class ResolveTicketEmbed(discord.Embed):
    message_localization: dict[LocaleEnum, str] = {
        LocaleEnum.ru: 'Вопрос был помечен как "Решенный" агентом {resolve_by_mention}.\n'
        '{ticket_author_mention}, уточните пожалуйста был ли решен Ваш вопрос, нажав на одну из кнопок ниже.',
        LocaleEnum.en: 'The issue was marked as “Resolved” by the agent {resolve_by_mention}.\n'
        '{ticket_author_mention}, please clarify whether your issue has been resolved '
        'by clicking on one of the buttons below.',
    }

    footer_localization: dict[LocaleEnum, str] = {
        LocaleEnum.ru: f'Тикет автоматически закроется через {HOURS_TO_CLOSE_TICKET_MARK_AS_RESOLVED} часов',
        LocaleEnum.en: f'The ticket will automatically close after {HOURS_TO_CLOSE_TICKET_MARK_AS_RESOLVED} hours',
    }

    @classmethod
    def build(cls, resolved_by: discord.Member, ticket_author_id: int, locale: LocaleEnum) -> Self:
        embed = cls(
            color=MAIN_COLOR,
            timestamp=datetime.datetime.now(tz=settings.TIMEZONE),
        )
        message = cls.message_localization[locale].format(
            resolve_by_mention=resolved_by.mention,
            ticket_author_mention=mention_user(ticket_author_id),
        )
        embed.add_field(name='', value=message)
        embed.set_footer(text=cls.footer_localization[locale])
        return embed


class MarkedAsResolvedTicketEmbed(discord.Embed):
    message_localization: dict[LocaleEnum, str] = {
        LocaleEnum.ru: 'Вопрос был отмечен автором как решённый.',
        LocaleEnum.en: 'The issue was marked by the author as resolved.',
    }

    @classmethod
    def build(cls, locale: LocaleEnum) -> Self:
        embed = cls(
            color=MAIN_COLOR,
            timestamp=datetime.datetime.now(tz=settings.TIMEZONE),
        )
        message = cls.message_localization[locale]

        embed.add_field(name='', value=message)
        return embed


class MarkedAsNoResolvedTicketEmbed(discord.Embed):
    message_localization: dict[LocaleEnum, str] = {
        LocaleEnum.ru: 'Вопрос был отмечен как нерешенный {no_resolve_by_mention}',
        LocaleEnum.en: 'The issue was marked as unresolved by {no_resolve_by_mention}',
    }

    @classmethod
    def build(cls, no_resolver_by: discord.Member, locale: LocaleEnum) -> Self:
        embed = cls(
            color=MAIN_COLOR,
            timestamp=datetime.datetime.now(tz=settings.TIMEZONE),
        )
        message = cls.message_localization[locale].format(
            no_resolve_by_mention=no_resolver_by.mention,
        )

        embed.add_field(name='', value=message)
        return embed
