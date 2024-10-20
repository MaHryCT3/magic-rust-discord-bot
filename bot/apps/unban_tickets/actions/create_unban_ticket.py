import datetime
from dataclasses import dataclass

import discord

from bot.apps.unban_tickets.actions.create_ticket_mixin import CreateTicketMixin
from bot.apps.unban_tickets.embeds import UnbanTicketEmbed
from bot.apps.unban_tickets.errors import SteamIDIsNotValid
from bot.apps.unban_tickets.services.unban_tickets import (
    UnbanTicketsService,
    UnbanTicketsStatus,
    UnbanTicketStruct,
)
from bot.apps.unban_tickets.ui.moderate_ticket_view import ModerateDiscordView
from bot.config import settings
from bot.dynamic_settings import dynamic_settings
from core.actions.abstract import AbstractAction
from core.api_clients.steam import SteamAPI, SteamProfileValidator
from core.localization import LocaleEnum


@dataclass
class CreateUnbanTicket(CreateTicketMixin, AbstractAction):
    guild: discord.Guild
    user: discord.User
    steam_id: str
    reason: str
    locale: LocaleEnum

    async def validate(self) -> None:
        await self._validate_on_ticket_exists(self.user)
        await self._validate_user_on_cooldown(self.user, self.locale)

        steam_id = await SteamProfileValidator(SteamAPI(settings.STEAM_API_TOKEN)).validate(
            self.steam_id,
            validate_on_exists=True,
        )
        if not steam_id:
            raise SteamIDIsNotValid(locale=self.locale)
        else:
            self.steam_id = steam_id

    async def action(self):
        await self._create_ticket()
        await self._send_ticket_to_moderate()

    async def _create_ticket(self):
        unban_ticket = UnbanTicketStruct(
            user_id=self.user.id,
            steam_id=self.steam_id,
            locale=self.locale,
            reason=self.reason,
            status=UnbanTicketsStatus.AWAITING,
            created_at=datetime.datetime.now(tz=settings.TIMEZONE).timestamp(),
        )
        await UnbanTicketsService().set_ticket(unban_ticket)

    async def _send_ticket_to_moderate(self):
        channel = await self.guild.fetch_channel(
            dynamic_settings.unban_ticket_channel_id,
        )
        embed = UnbanTicketEmbed.build(
            user=self.user,
            steam_id=self.steam_id,
            reason=self.reason,
            status=UnbanTicketsStatus.AWAITING,
        )
        await channel.send(
            view=ModerateDiscordView(steam_id=self.steam_id),
            content=self.user.mention,
            embed=embed,
        )
