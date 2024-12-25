import dataclasses
import datetime
from abc import ABC
from dataclasses import dataclass
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
from bot.constants import DATETIME_FORMAT
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
        except discord.Forbidden as exception:
            if self.moderate_message:
                await self._add_to_message_information_about_failed_to_send_result(self.moderate_message)
            else:
                raise UserDmIsClosed() from exception

        await unban_ticket_cooldown.set_user_cooldown(
            self.user_id,
            cooldown_in_seconds=UNBAN_TICKET_COOLDOWN_SECONDS,
        )

    async def _close_ticket(self, ticket: UnbanTicketStruct, moderate_message: discord.Message):
        embed = moderate_message.embeds[0]
        embed = UnbanTicketEmbed.from_dict(embed.to_dict())
        embed.timestamp = datetime.datetime.now(tz=settings.TIMEZONE)
        embed.set_status(ticket.status).set_reviewed_by(self.initiator_user)

        moderate_message.embeds[0] = embed
        await moderate_message.edit(
            view=None,
            embeds=moderate_message.embeds,
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


@dataclass
class NeedToAddInFriendAction(AbstractAction):
    user_id: int
    bot: MagicRustBot
    add_in_friend: discord.User
    moderate_message: discord.Message | None = None

    message_localization: ClassVar[dict[LocaleEnum, str]] = {
        LocaleEnum.ru: 'Для продолжения процедуры разбана вам необходимо '
        'добавить в друзья модератора {moderator_mention}',
        LocaleEnum.en: 'You need to add the moderator {moderator_mention}'
        ' as a friend to continue the unban procedure .',
    }

    async def action(self) -> None:
        unban_ticket_service = UnbanTicketsService()

        ticket = await unban_ticket_service.get_by_user(self.user_id)
        if not ticket:
            raise UserDontHaveTicket()

        try:
            await self._send_message_to_user(ticket)
        except discord.Forbidden as ex:
            raise UserDmIsClosed() from ex

        await self._add_information_about_sent_friend_invite(self.moderate_message)

    async def _add_information_about_sent_friend_invite(self, message: discord.Message):
        # сейчас если тикет не закрыт там может быть только 1 ембед, в другом случае если их два
        # значит кто то уже пытался добавить в друзья, пробуем достать информацию.

        if len(message.embeds) == 2:  # noqa: PLR2004
            info_embed = message.embeds[1]
            exists_text = info_embed.fields[0].value
        else:
            exists_text = ''

        now_time = datetime.datetime.now(tz=settings.TIMEZONE).strftime(DATETIME_FORMAT)
        embed = discord.Embed(
            colour=discord.Color.red(),
        ).add_field(
            name='',
            value=f'{exists_text}\n{now_time} {self.add_in_friend.mention} попросил игрока добавить его в друзья',
        )

        finally_embeds = message.embeds.copy()
        if exists_text:
            finally_embeds[1] = embed
        else:
            finally_embeds.append(embed)

        await message.edit(embeds=finally_embeds)

    async def _send_message_to_user(self, ticket: UnbanTicketStruct):
        user = await self.bot.fetch_user(ticket.user_id)
        message = self.message_localization[ticket.locale].format(moderator_mention=self.add_in_friend.mention)
        await user.send(message)
