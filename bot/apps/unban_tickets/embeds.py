import datetime
from typing import Self

import discord

from bot.apps.unban_tickets.constants import UNBAN_TICKET_COLOR
from bot.apps.unban_tickets.services.unban_tickets import (
    UnbanTicketsStatus,
)
from core.emojis import Emojis


class UnbanTicketEmbed(discord.Embed):
    status_emoji: dict[UnbanTicketsStatus, str] = {
        UnbanTicketsStatus.APPROVED: Emojis.ACCEPT,
        UnbanTicketsStatus.AWAITING: Emojis.AWAITING,
        UnbanTicketsStatus.REJECTED: Emojis.REJECT,
    }

    def set_status(self, status: UnbanTicketsStatus) -> Self:
        status_index = 2
        status_field_kwargs = {
            'name': 'Статус',
            'value': self.status_emoji[status],
            'inline': False,
        }
        if len(self.fields) < status_index + 1:
            return self.insert_field_at(status_index, **status_field_kwargs)
        return self.set_field_at(status_index, **status_field_kwargs)

    def set_reviewed_by(self, reviewed_by: discord.User) -> Self:
        return self.set_footer(
            text=reviewed_by.name,
            icon_url=getattr(reviewed_by.avatar, 'url', None),
        )

    @classmethod
    def build(
        cls,
        user: discord.User,
        steam_id: str,
        reason: str,
        status: UnbanTicketsStatus,
        reviewed_by: discord.User | None = None,
        reviewed_at: datetime.datetime | None = None,
    ) -> Self:
        embed = cls(color=UNBAN_TICKET_COLOR, timestamp=reviewed_at)
        embed.set_author(
            name=user.name,
            icon_url=getattr(user.avatar, 'url', None),
        )
        embed.add_field(name='SteamID', value=steam_id)
        embed.add_field(name='Причина', value=reason)
        embed.set_status(status)

        if reviewed_by:
            embed.set_reviewed_by(reviewed_by)

        return embed
