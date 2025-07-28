import asyncio
import datetime
import io
from collections import Counter
from dataclasses import dataclass, field
from functools import cached_property

import discord
import sentry_sdk
from chat_exporter.construct.transcript import Transcript

from bot.apps.tickets.services.opened_tickets import (
    OpenedTicketsService,
    OpenedTicketStruct,
)
from bot.apps.tickets.services.review_awaiting import (
    ReviewAwaitingService,
    ReviewAwaitingStruct,
)
from bot.apps.tickets.services.ticket_history_api import TicketHistoryAPI
from bot.apps.tickets.ui.ticket_header.header_embed import TicketHeaderEmbed
from bot.apps.tickets.ui.ticket_header.score_view import TicketScoreView
from bot.apps.tickets.utils import get_channel_ticket_moderators
from bot.config import settings
from bot.dynamic_settings import dynamic_settings
from core.actions.abstract import AbstractAction
from core.logger import logger
from core.shortcuts import get_or_fetch_member


@dataclass
class CloseTicketAction(AbstractAction):
    channel: discord.TextChannel
    closed_by: discord.Member | None = None

    _opened_tickets_service: OpenedTicketsService = field(
        default_factory=OpenedTicketsService,
        init=False,
    )
    _ticket_history_api: TicketHistoryAPI = field(
        default_factory=TicketHistoryAPI,
        init=False,
    )
    _awaiting_review_service: ReviewAwaitingService = field(
        default_factory=ReviewAwaitingService,
        init=False,
    )

    @cached_property
    def closed_at(self) -> datetime.datetime:
        return datetime.datetime.now(tz=settings.TIMEZONE)

    @cached_property
    def ticket_moderators(self):
        return get_channel_ticket_moderators(self.channel)

    async def action(self) -> None:
        ticket = await self._opened_tickets_service.get_user_ticket_by_channel_id(self.channel.id)
        if not ticket:
            # не вижу смысла заводить ошибку это по сути невозможный кейс, но просто на всякий
            raise Exception()

        try:
            ticket_user = await get_or_fetch_member(self.channel.guild, ticket.user_id)
        except discord.NotFound:
            # если его например кикнули с канала после создания тикета, то мы его не найдем
            ticket_user = None

        if ticket_user:
            await self._close_ticket_for_user(ticket_user)

        # сохраняем сообщения, для сохранения статистики и выгрузки истории чатов
        chat_messages = await self._get_chat_messages()
        chat_transcripter = self._get_transcripter(chat_messages)
        exported_chat = await chat_transcripter.export()

        transcript_url = None
        try:
            transcript_url = await self._save_ticket_history_and_get_transcript_url(
                ticket=ticket,
                messages=chat_messages,
                ticket_history_html=exported_chat.html,
            )
        except Exception as ex:
            sentry_sdk.capture_exception(ex)
            logger.exception(
                'Exception when trying saving ticket history',
                exc_info=True,
            )

        ended_embed = self._get_closed_ticket_embed(
            ticket,
            ticket_user,
            transcript_link=transcript_url,
        )
        # отправляем в текущний чат ембед об окончании
        await self.channel.send(embed=ended_embed)

        # отравляем историю в чат для логов тикетов
        await self._send_chat_history(ticket, ended_embed, exported_chat.html)

        # удаляем запись из редиса о тикете
        await self._opened_tickets_service.delete_user_ticket(ticket)

        await asyncio.sleep(2.5)
        await self.channel.delete(reason='Ticket closed')

        # отправляем пользователю историю тикета, если не удалось загрузить историю тикета, отправляем просто файлом
        if ticket_user:
            if not transcript_url:
                await self._send_ticket_to_member(
                    ticket,
                    ticket_user,
                    ended_embed,
                    chat_history_html=exported_chat.html,
                )
            else:
                await self._send_ticket_to_member(
                    ticket,
                    ticket_user,
                    ended_embed,
                )

    async def _get_chat_messages(self) -> list[discord.Message]:
        return [message async for message in self.channel.history(limit=None)]

    def _get_transcripter(self, messages: list[discord.Message]) -> Transcript:
        return Transcript(
            channel=self.channel,
            limit=None,
            messages=messages,
            pytz_timezone='UTC',
            military_time=True,
            fancy_times=True,
            before=None,
            after=None,
            support_dev=True,
            bot=None,
            attachment_handler=None,
        )

    async def _save_ticket_history_and_get_transcript_url(
        self,
        ticket: OpenedTicketStruct,
        messages: list[discord.Message],
        ticket_history_html: str,
    ) -> str:
        await self._save_ticket_history(ticket, messages, ticket_history_html)
        return await self._ticket_history_api.get_ticket_history_logs_file_url(ticket.ticket_number)

    async def _save_ticket_history(
        self,
        ticket: OpenedTicketStruct,
        messages: list[discord.Message],
        ticket_history_html: str,
    ):
        moderators_count_message = Counter(
            [message.author.id for message in messages if message.author in self.ticket_moderators]
        )
        last_moderator_message_id = None
        for message in messages:
            if message.author in self.ticket_moderators:
                last_moderator_message_id = message.author.id
                break

        moderators_sorted_by_messages_count = [
            moderator_id for (moderator_id, count) in moderators_count_message.most_common()
        ]

        await self._ticket_history_api.create_ticket_history(
            last_moderator_answer_id=last_moderator_message_id,
            moderators_discord_ids=moderators_sorted_by_messages_count,
            html_logs=ticket_history_html,
            author_discord_id=ticket.user_id,
            start_datetime=ticket.created_at,
            end_datetime=self.closed_at,
            ticket_number=ticket.ticket_number,
        )

    def _get_closed_ticket_embed(
        self,
        ticket: OpenedTicketStruct,
        ticket_user: discord.Member | None,
        transcript_link: str | None = None,
    ):
        return TicketHeaderEmbed.build(
            locale=ticket.locale,
            ticket_number=ticket.ticket_number,
            created_at=ticket.created_at,
            user_steam=ticket.user_steam,
            description=ticket.description,
            opened_by=ticket_user,
            closed_by=self.closed_by,
            closed_at=self.closed_at,
            transcript_url=transcript_link,
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
        ended_embed: discord.Embed,
        chat_history_html: str | None = None,
    ):
        chat_history_file = None
        if chat_history_html:
            chat_history_file = discord.File(
                io.BytesIO(chat_history_html.encode()),
                filename=f'history-{ticket.ticket_number}.html',
            )

        member_ticket_view = TicketScoreView(
            locale=ticket.locale,
            ticket_number=ticket.ticket_number,
        )
        try:
            message = await ticket_user.send(
                embed=ended_embed,
                file=chat_history_file,
                view=member_ticket_view,
            )
        except discord.Forbidden:
            logger.info(f'Не удалось отправить историю тикета #{ticket.ticket_number} в личку, так как она закрыта')
            return

        await self._add_member_review_awaiting(
            ticket=ticket,
            review_message_id=message.id,
        )

    async def _add_member_review_awaiting(self, ticket: OpenedTicketStruct, review_message_id: int):
        review_awaiting = ReviewAwaitingStruct(
            message_id=review_message_id,
            user_id=ticket.user_id,
            ticket_number=ticket.ticket_number,
            created_at=self.closed_at,
            locale=ticket.locale,
        )
        await self._awaiting_review_service.add_review_awaiting(review_awaiting)
