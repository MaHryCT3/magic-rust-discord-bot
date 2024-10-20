import dataclasses
import datetime
from abc import ABC
from typing import ClassVar

import discord

from bot import MagicRustBot
from bot.apps.unban_tickets.constants import UNBAN_TICKET_COOLDOWN_SECONDS
from bot.apps.unban_tickets.cooldowns import unban_ticket_cooldown
from bot.apps.unban_tickets.embeds import UnbanTicketEmbed
from bot.apps.unban_tickets.errors import UserDmIsClosed, UserDontHaveTicket
from bot.apps.unban_tickets.services.unban_tickets import (
    UnbanTicketsService,
    UnbanTicketsStatus,
    UnbanTicketStruct,
)
from bot.config import settings
from core.actions.abstract import AbstractAction
from core.emojis import Emojis
from core.localization import LocaleEnum


@dataclasses.dataclass
class ModerateUnbanTicket(AbstractAction, ABC):
    user_id: int
    bot: MagicRustBot
    initiator_user: discord.User
    moderate_message: discord.Message | None = None

    result_message: ClassVar[dict[LocaleEnum, str]]
    ticket_status: ClassVar[UnbanTicketsStatus]

    async def action(self):
        unban_ticket_service = UnbanTicketsService()

        ticket = await unban_ticket_service.get_by_user(self.user_id)
        if not ticket:
            raise UserDontHaveTicket()

        ticket.status = self.ticket_status
        await unban_ticket_service.set_ticket(ticket)

        if self.moderate_message:
            await self._close_ticket(ticket, self.moderate_message)
        try:
            await self._send_result_to_user(ticket, self.bot)
        except discord.Forbidden:
            if self.moderate_message:
                await self._add_to_message_information_about_failed_to_send_result(self.moderate_message)
            else:
                raise UserDmIsClosed() from None

        await unban_ticket_cooldown.set_user_cooldown(
            self.user_id,
            cooldown_in_seconds=UNBAN_TICKET_COOLDOWN_SECONDS,
        )

    async def _close_ticket(self, ticket: UnbanTicketStruct, moderate_message: discord.Message):
        embed = moderate_message.embeds[0]
        embed = UnbanTicketEmbed.from_dict(embed.to_dict())
        embed.timestamp = datetime.datetime.now(tz=settings.TIMEZONE)
        embed.set_status(ticket.status).set_reviewed_by(self.initiator_user)

        moderate_message.embeds = [embed]
        await moderate_message.edit(
            view=None,
            embeds=[embed],
        )

    async def _send_result_to_user(self, ticket: UnbanTicketStruct, bot: MagicRustBot):
        user = await bot.fetch_user(ticket.user_id)
        message = self.result_message[ticket.locale]
        await user.send(message)

    async def _add_to_message_information_about_failed_to_send_result(self, moderate_message: discord.Message):
        failed_embed = discord.Embed(color=discord.Color.red(), title=f'{Emojis.WARNING}Ошибка').add_field(
            name='',
            value='Заявка рассмотрена, '
            'но результат не удалось отправить пользователю так как он закрыл личные сообщения с ботом',
        )
        await moderate_message.edit(embeds=moderate_message.embeds + [failed_embed])


class ApproveUnbanTicket(ModerateUnbanTicket):
    user_id: int
    bot: MagicRustBot
    moderate_message: discord.Message
    initiator_user: discord.User

    result_message: ClassVar[dict[LocaleEnum, str]] = {
        LocaleEnum.ru: 'Благодарим Вас за подачу заявки. Ваш аккаунт был разблокирован. Приятной игры!',
        LocaleEnum.en: 'Thank you for submitting your unban request. Your account has been unban. Enjoy your game!',
    }
    ticket_status: ClassVar[UnbanTicketsStatus] = UnbanTicketsStatus.APPROVED


class RejectUnbanTicket(ModerateUnbanTicket):
    user_id: int
    bot: MagicRustBot
    moderate_message: discord.Message
    initiator_user: discord.User

    result_message: ClassVar[dict[LocaleEnum, str]] = {
        LocaleEnum.ru: 'Увы, но в результате рассмотрения Вашей заявки мы пришли к выводу, '
        'что разблокировка Вашего аккаунта пока не представляется возможной.',
        LocaleEnum.en: 'Alas, as a result of reviewing your unban request we have come '
        'to the conclusion that unban your account is not yet possible.',
    }
    ticket_status: ClassVar[UnbanTicketsStatus] = UnbanTicketsStatus.REJECTED
