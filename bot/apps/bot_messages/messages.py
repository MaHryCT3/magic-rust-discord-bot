import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands

from bot import MagicRustBot
from bot.apps.bot_messages.autocomplete import (
    parse_autocomplete_time,
    select_time_autocomplete,
)
from bot.apps.bot_messages.exceptions import BotMessageError
from bot.apps.bot_messages.modals import AddQueueMessageModal, SendMessageByBotModal
from bot.apps.bot_messages.services import DelayedMessageService
from bot.constants import DATETIME_FORMAT


class BotMessagesCommandsCog(commands.Cog):
    message_group = SlashCommandGroup(
        'm',
        description='Сообщения от бота',
        default_member_permissions=discord.Permissions(
            administrator=True,
            ban_members=True,
        ),
        guild_only=True,
    )

    def __init__(self, bot: MagicRustBot, delayed_message_service: DelayedMessageService) -> None:
        self.bot = bot
        self.delayed_message_service = delayed_message_service

    @message_group.command(description='Отправка сообщений в канал')
    async def send(
        self,
        ctx: discord.ApplicationContext,
        send_time: discord.Option(
            str,
            required=False,
            autocomplete=select_time_autocomplete,
            description='Отложенная отправка сообщения. Форматы: "14:00" или "06.07.2024 13:00"',
        ),
        text_before: discord.Option(
            str,
            required=False,
            autocomplete=discord.utils.basic_autocomplete(
                ['@everyone', '@here'],
            ),
            description='Текст перед основным текстом, который заполняется далее.',
        ),
    ):
        send_time = parse_autocomplete_time(send_time)
        if send_time:
            modal = AddQueueMessageModal(
                title=f'Сообщение на {send_time.strftime(DATETIME_FORMAT)}',
                delayed_message_service=self.delayed_message_service,
                text_before=text_before,
                send_time=send_time,
            )
        else:
            modal = SendMessageByBotModal(
                title='Отправка сообщения от имени бота',
                delayed_message_service=self.delayed_message_service,
                text_before=text_before,
                send_time=send_time,
            )
        await ctx.send_modal(modal)

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: BotMessageError):
        if isinstance(error, BotMessageError):
            return await ctx.respond(error.message, ephemeral=True)
        raise error
