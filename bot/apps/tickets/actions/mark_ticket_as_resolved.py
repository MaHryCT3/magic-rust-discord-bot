import datetime
from dataclasses import dataclass, field

import discord

from bot.apps.tickets.errors import NoTicketFound
from bot.apps.tickets.overwrites import user_ticket_overwrites_no_send_message
from bot.apps.tickets.services.opened_tickets import (
    OpenedTicketsService,
    OpenedTicketStruct,
)
from bot.apps.tickets.ui.resolve_ticket.embeds import ResolveTicketEmbed
from bot.apps.tickets.ui.resolve_ticket.views import ResolveTicketView
from bot.config import settings
from core.actions.abstract import AbstractAction


@dataclass
class MarkTicketAsResolvedAction(AbstractAction):
    channel: discord.TextChannel
    resolved_by: discord.Member

    _opened_ticket: OpenedTicketStruct | None = field(init=False, default=None)

    async def load_data(self):
        self._opened_ticket = await OpenedTicketsService().get_user_ticket_by_channel_id(self.channel.id)

    async def validate(self):
        if not self._opened_ticket:
            raise NoTicketFound()

    async def action(self):
        await self._send_resolve_view()
        await self._mark_ticket_as_resolved()

        ticket_user = await self.channel.guild.fetch_member(self._opened_ticket.user_id)
        if ticket_user:
            await self._close_ticket_message_for_user(ticket_user)

    async def _send_resolve_view(self):
        embed = ResolveTicketEmbed.build(
            resolved_by=self.resolved_by,
            ticket_author_id=self._opened_ticket.user_id,
            locale=self._opened_ticket.locale,
        )
        view = ResolveTicketView(self._opened_ticket.locale)
        await self.channel.send(
            embed=embed,
            view=view,
        )

    async def _close_ticket_message_for_user(self, ticket_user: discord.Member):
        await self.channel.set_permissions(
            target=ticket_user,
            overwrite=user_ticket_overwrites_no_send_message,
        )

    async def _mark_ticket_as_resolved(self):
        self._opened_ticket.resolved_at = datetime.datetime.now(tz=settings.TIMEZONE)
        await OpenedTicketsService().set_user_ticket(self._opened_ticket)
