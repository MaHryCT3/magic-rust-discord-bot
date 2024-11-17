import asyncio
import datetime
import io
from dataclasses import dataclass

import chat_exporter
import discord

from bot.apps.tickets.services.opened_tickets import (
    OpenedTicketsService,
    OpenedTicketStruct,
)
from bot.apps.tickets.ui.ticket_header.embed import TicketHeaderEmbed
from bot.config import settings
from bot.dynamic_settings import dynamic_settings
from core.actions.abstract import AbstractAction
from core.logger import logger


@dataclass
class CloseTicketAction(AbstractAction):
    channel: discord.TextChannel
    closed_by: discord.Member

    def __post_init__(self):
        self._opened_tickets = OpenedTicketsService()

    async def action(self) -> None:
        ticket = await self._opened_tickets.get_user_ticket_by_channel_id(self.channel.id)
        if not ticket:
            # не вижу смысла заводить ошибку это по сути невозможный кейс, но просто на всякий
            raise Exception()

        try:
            ticket_user = await self.channel.guild.fetch_member(ticket.user_id)
        except discord.NotFound:
            # если его например кикнули с канала после создания тикета, то мы его не найдем
            ticket_user = None

        if ticket_user:
            await self._close_ticket_for_user(ticket_user)

        exported_chat = await chat_exporter.export(channel=self.channel)

        ended_embed = self._get_closed_ticket_embed(ticket, ticket_user)
        # отправляем в текущний чат ембед об окончании
        await self.channel.send(embed=ended_embed)

        # отравляем историю в чат для логов тикетов
        await self._send_chat_history(ticket, ended_embed, exported_chat)

        # удаляем запись из редиса о тикете
        await self._opened_tickets.delete_user_ticket(ticket)

        await asyncio.sleep(30)
        await self.channel.delete(reason='Ticket closed')

        # отправляем пользователю историю тикета
        try:
            await self._send_ticket_to_member(ticket, ticket_user, exported_chat, ended_embed)
        except discord.Forbidden:
            logger.info(f'Не удалось отправить историю тикета #{ticket.ticket_number} в личку, так как она закрыта')

    def _get_closed_ticket_embed(self, ticket: OpenedTicketStruct, ticket_user: discord.Member):
        return TicketHeaderEmbed.build(
            locale=ticket.locale,
            ticket_number=ticket.ticket_number,
            created_at=ticket.created_at,
            user_steam=ticket.user_steam,
            description=ticket.description,
            opened_by=ticket_user,
            closed_by=self.closed_by,
            closed_at=datetime.datetime.now(tz=settings.TIMEZONE),
        )

    async def _send_chat_history(
        self,
        ticket: OpenedTicketStruct,
        closed_embed: discord.Embed,
        chat_history_html: str,
    ):
        history_channel_id = dynamic_settings.ticket_history_channel_id
        ticket_history_channel = await self.channel.guild.fetch_channel(history_channel_id)

        chat_history_file = discord.File(
            io.BytesIO(chat_history_html.encode()),
            filename=f'history-{ticket.ticket_number}.html',
        )

        await ticket_history_channel.send(
            embed=closed_embed,
            file=chat_history_file,
        )

    async def _close_ticket_for_user(self, ticket_user: discord.Member):
        await self.channel.set_permissions(
            target=ticket_user,
            overwrite=discord.PermissionOverwrite(view_channel=False),
        )

    async def _send_ticket_to_member(
        self,
        ticket: OpenedTicketStruct,
        ticket_user: discord.Member,
        chat_history_html: str,
        ended_embed: discord.Embed,
    ):
        chat_history_file = discord.File(
            io.BytesIO(chat_history_html.encode()),
            filename=f'history-{ticket.ticket_number}.html',
        )
        await ticket_user.send(
            embed=ended_embed,
            file=chat_history_file,
        )
