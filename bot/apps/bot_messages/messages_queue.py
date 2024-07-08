import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands, tasks

from bot import MagicRustBot
from bot.apps.bot_messages.exceptions import BotMessageError
from bot.apps.bot_messages.paginator import QueueMessagePaginator
from bot.apps.bot_messages.services import DelayedMessage, DelayedMessageService
from bot.apps.bot_messages.utils import send_delayed_message
from bot.config import logger


class MessageQueueCog(commands.Cog):
    queue_group = SlashCommandGroup(
        name='queue',
        description='Управление очередью сообщений',
        guild_only=True,
        default_member_permissions=discord.Permissions(
            administrator=True,
            ban_members=True,
        ),
    )

    def __init__(self, bot: MagicRustBot, delayed_message_service: DelayedMessageService):
        self.bot = bot
        self.delayed_message_service = delayed_message_service
        self.check_delayed_messages.start()

    @queue_group.command(description='Просмотреть очередь сообщений')
    async def show(self, ctx: discord.ApplicationContext):
        paginator = await QueueMessagePaginator.from_delayed_message_service(
            delayed_message_service=self.delayed_message_service,
        )
        await paginator.respond(ctx.interaction, ephemeral=True)

    @queue_group.command(description='Очистить очередь отложенных сообщений')
    async def clear(self, ctx: discord.ApplicationContext):
        logger.info(f'message queue was cleared by {ctx.user}:{ctx.user.id}')
        await self.delayed_message_service.clear_messages()
        await ctx.respond('Очередь на отложенные сообщения очищена', ephemeral=True)

    @tasks.loop(seconds=5)
    async def check_delayed_messages(self):
        logger.debug('checking delayed messages')
        messages_to_send = await self.delayed_message_service.get_messages_to_send()
        logger.debug(f'messages to send: {messages_to_send}')

        for message in messages_to_send:
            await send_delayed_message(message, self.bot)

    def _sort_delayed_messages(self, messages: list[DelayedMessage]):
        return sorted(messages, key=lambda message: message.send_time)

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: BotMessageError):
        if isinstance(error, BotMessageError):
            return await ctx.respond(error.message, ephemeral=True)
        raise error

    def cog_unload(self) -> None:
        self.check_delayed_messages.cancel()
