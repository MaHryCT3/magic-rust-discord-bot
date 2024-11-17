from dataclasses import dataclass, field
from functools import cached_property

import discord

from bot.apps.tickets.overwrites import user_ticket_overwrites
from bot.apps.tickets.services.opened_tickets import (
    OpenedTicketsService,
    OpenedTicketStruct,
)
from bot.apps.tickets.ui.resolve_ticket.embeds import MarkedAsNoResolvedTicketEmbed
from bot.dynamic_settings import dynamic_settings
from core.actions.abstract import AbstractAction
from core.shortcuts import get_or_fetch_member


@dataclass
class NoResolveTicketAction(AbstractAction):
    channel: discord.TextChannel
    resolve_by: discord.Member
    message: discord.Message

    _opened_ticket: OpenedTicketStruct | None = field(init=False, default=None)

    @cached_property
    def tickets_moderators_roles(self) -> list[discord.Role]:
        moderators_roles_ids = dynamic_settings.ticket_roles_ids
        return [role for role in self.channel.guild.roles if role.id in moderators_roles_ids]

    async def load_data(self):
        self._opened_ticket = await OpenedTicketsService().get_user_ticket_by_channel_id(self.channel.id)

    async def action(self):
        await self._clear_resolve_at()
        ticket_user = await get_or_fetch_member(self.channel.guild, self._opened_ticket.user_id)
        await self._open_chat_for_user(ticket_user)

        await self._add_no_resolved_message()

        mention_moderators = '\n'.join([role.mention for role in self.tickets_moderators_roles])
        await self.channel.send(mention_moderators)

    async def _open_chat_for_user(self, ticket_user: discord.Member):
        await self.channel.set_permissions(
            target=ticket_user,
            overwrite=user_ticket_overwrites,
        )

    async def _add_no_resolved_message(self):
        no_resolve_embed = MarkedAsNoResolvedTicketEmbed.build(
            no_resolver_by=self.resolve_by,
            locale=self._opened_ticket.locale,
        )

        await self.message.edit(
            embeds=self.message.embeds + [no_resolve_embed],
            view=None,
        )

    async def _clear_resolve_at(self):
        self._opened_ticket.resolved_at = None
        await OpenedTicketsService().set_user_ticket(self._opened_ticket)
