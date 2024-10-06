import datetime
from dataclasses import dataclass
from functools import cached_property

import discord

from bot.apps.tickets.errors import UserAlreadyHaveTicket
from bot.apps.tickets.services.opened_tickets import (
    OpenedTicketsService,
    OpenedTicketStruct,
)
from bot.apps.tickets.services.ticket_counter import TicketCounter
from bot.apps.tickets.ui.ticket_header import TicketHeaderEmbed, TicketHeaderView
from bot.config import settings
from bot.dynamic_settings import dynamic_settings
from core.actions.abstract import AbstractAction
from core.localization import LocaleEnum


@dataclass
class CreateTicketAction(AbstractAction[discord.TextChannel]):
    locale: LocaleEnum
    guild: discord.Guild
    member: discord.Member
    user_steam: str
    description: str

    @cached_property
    def created_at(self):
        return datetime.datetime.now(tz=settings.TIMEZONE)

    def __post_init__(self):
        self._ticket_counter = TicketCounter()
        self._opened_tickets = OpenedTicketsService()

    async def validate(self):
        user_ticket = await self._opened_tickets.get_user_ticket_by_user_id(self.member.id)
        if user_ticket:
            channel = await self.guild.fetch_channel(user_ticket.channel_id)
            raise UserAlreadyHaveTicket(self.locale, ticket_channel_mention=channel.mention)

    async def action(self) -> discord.TextChannel:
        category = self._get_ticket_category()
        ticket_number = await self._ticket_counter.increase()

        ticket_channel = await self.create_ticket_channel(category, ticket_number)
        await self.send_header_message(ticket_channel, ticket_number)
        user_ticket = OpenedTicketStruct(
            locale=self.locale,
            user_id=self.member.id,
            ticket_number=ticket_number,
            channel_id=ticket_channel.id,
            created_at=self.created_at,
            user_steam=self.user_steam,
            description=self.description,
        )
        await self._opened_tickets.set_user_ticket(user_ticket)

        return ticket_channel

    def _get_ticket_category(self) -> discord.CategoryChannel:
        ticket_category_id = dynamic_settings.ticket_category_id
        for category in self.guild.categories:
            if category.id == ticket_category_id:
                return category

        raise AssertionError('Не получилось найти категорию для тикетов')

    async def create_ticket_channel(self, category: discord.CategoryChannel, ticket_number: int):
        room_name = f'ticket-{ticket_number}'

        member_permissions = discord.PermissionOverwrite(
            view_channel=True,
            read_message_history=True,
            send_messages=True,
        )
        everyone_permission = discord.PermissionOverwrite(
            view_channel=False,
        )

        channel = await self.guild.create_text_channel(
            name=room_name,
            category=category,
            overwrites={
                self.guild.default_role: everyone_permission,
                self.member: member_permissions,
            },
        )
        return channel

    async def send_header_message(self, channel: discord.TextChannel, ticket_number: int) -> discord.Message:
        header_embed = TicketHeaderEmbed.build(
            locale=self.locale,
            ticket_number=ticket_number,
            created_at=self.created_at,
            opened_by=self.member,
            user_steam=self.user_steam,
            description=self.description,
        )
        header_view = TicketHeaderView(locale=self.locale)

        await channel.send(
            embed=header_embed,
            view=header_view,
        )
