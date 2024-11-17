from dataclasses import dataclass, field

import discord

from bot.apps.tickets.actions.close_ticket import CloseTicketAction
from bot.apps.tickets.errors import ActionAllowOnlyForTicketAuthorError
from bot.apps.tickets.services.opened_tickets import (
    OpenedTicketsService,
    OpenedTicketStruct,
)
from bot.apps.tickets.ui.resolve_ticket.embeds import MarkedAsResolvedTicketEmbed
from core.actions.abstract import AbstractAction


@dataclass
class ResolveTicketAction(AbstractAction):
    channel: discord.TextChannel
    resolve_by: discord.Member
    message: discord.Message

    _opened_ticket: OpenedTicketStruct | None = field(init=False, default=None)

    async def load_data(self):
        self._opened_ticket = await OpenedTicketsService().get_user_ticket_by_channel_id(self.channel.id)

    async def validate(self):
        if self.resolve_by.id != self._opened_ticket.user_id:
            raise ActionAllowOnlyForTicketAuthorError()

    async def action(self):
        resolved_embed = MarkedAsResolvedTicketEmbed.build(locale=self._opened_ticket.locale)
        await self.message.edit(
            embeds=self.message.embeds + [resolved_embed],
            view=None,
        )

        close_ticket_action = CloseTicketAction(
            channel=self.channel,
            closed_by=self.resolve_by,
        )
        await close_ticket_action.execute()
