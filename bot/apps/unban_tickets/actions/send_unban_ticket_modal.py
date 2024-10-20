from dataclasses import dataclass

import discord

from bot import MagicRustBot
from bot.apps.unban_tickets.actions.create_ticket_mixin import CreateTicketMixin
from bot.apps.unban_tickets.errors import (
    UserDmIsClosed,
)
from bot.apps.unban_tickets.ui.ticket_modal import CreateTicketModal
from core.actions.abstract import AbstractAction
from core.localization import LocaleEnum
from core.shortcuts import can_dm_user


@dataclass
class SendUnbanTicketModal(CreateTicketMixin, AbstractAction):
    locale: LocaleEnum
    interaction: discord.Interaction

    @property
    def user(self) -> discord.User:
        return self.interaction.user

    @property
    def bot(self) -> MagicRustBot:
        return self.interaction.client

    async def validate(self) -> None:
        await self._validate_on_ticket_exists(self.user)
        await self._validate_user_on_cooldown(self.user, self.locale)

        if not await can_dm_user(self.user):
            raise UserDmIsClosed(user=self.user, bot_id=self.bot.application_id, locale=self.locale)

    async def action(self):
        modal = CreateTicketModal(locale=self.locale)
        await self.interaction.response.send_modal(modal)
