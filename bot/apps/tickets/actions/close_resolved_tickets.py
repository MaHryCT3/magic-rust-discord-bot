import datetime
from dataclasses import dataclass, field

import discord
import sentry_sdk
from discord import NotFound

from bot.apps.tickets.actions.close_ticket import CloseTicketAction
from bot.apps.tickets.constants import MINUTES_TO_CLOSE_TICKET_MARKED_AS_RESOLVED
from bot.apps.tickets.services.opened_tickets import (
    OpenedTicketsService,
    OpenedTicketStruct,
)
from bot.config import settings
from core.actions.abstract import AbstractAction
from core.shortcuts import get_or_fetch_channel, get_or_fetch_member


@dataclass
class CloseResolvedTicketsAction(AbstractAction):
    """
    Закрывает тикеты, которые уже `HOURS_TO_CLOSE_TICKET_MARK_AS_RESOLVED` помечены как решенные агентом поддержки
    """

    guild: discord.Guild

    _opened_tickets_service: OpenedTicketsService = field(
        default_factory=OpenedTicketsService,
        init=False,
    )

    async def action(self):

        tickets = await self._opened_tickets_service.get_all_tickets()
        for ticket in tickets:
            if ticket.resolved_at is None:
                continue

            remove_ticket_at = ticket.resolved_at + datetime.timedelta(
                minutes=MINUTES_TO_CLOSE_TICKET_MARKED_AS_RESOLVED
            )
            if datetime.datetime.now(tz=settings.TIMEZONE) >= remove_ticket_at:
                try:
                    await self._close_ticket(ticket)
                except NotFound:
                    await self._opened_tickets_service.delete_user_ticket(ticket)
                except Exception as ex:
                    if settings.DEBUG:
                        raise ex from None

                    sentry_sdk.capture_exception(ex)

    async def _close_ticket(self, ticket: OpenedTicketStruct):
        channel = await get_or_fetch_channel(self.guild, ticket.channel_id)
        try:
            closed_by = await get_or_fetch_member(self.guild, ticket.user_id)
        except NotFound:
            closed_by = None
        await CloseTicketAction(
            channel=channel,
            closed_by=closed_by,
        ).execute()
