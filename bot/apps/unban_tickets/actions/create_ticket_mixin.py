import discord

from bot.apps.unban_tickets.constants import UNBAN_TICKET_COOLDOWN_SECONDS
from bot.apps.unban_tickets.cooldowns import unban_ticket_cooldown
from bot.apps.unban_tickets.errors import (
    AlreadyHaveUnbanTicketError,
    UnbanTicketCooldownError,
)
from bot.apps.unban_tickets.services.unban_tickets import (
    UnbanTicketsService,
    UnbanTicketsStatus,
)
from core.localization import LocaleEnum


class CreateTicketMixin:
    @staticmethod
    async def _validate_on_ticket_exists(user: discord.User) -> None:
        ticket = await UnbanTicketsService().get_by_user(user.id)
        if ticket and ticket.status == UnbanTicketsStatus.AWAITING:
            raise AlreadyHaveUnbanTicketError(user=user, ticket=ticket)

    @staticmethod
    async def _validate_user_on_cooldown(user: discord.User, locale: LocaleEnum) -> None:
        retry_after = await unban_ticket_cooldown.get_cooldown_end_at(user.id, UNBAN_TICKET_COOLDOWN_SECONDS)
        if retry_after:
            raise UnbanTicketCooldownError(retry_after, locale)
