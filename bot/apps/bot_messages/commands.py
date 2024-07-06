import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands, tasks

from bot import MagicRustBot
from bot.apps.bot_messages.autocomplete import (
    parse_complete_time,
    select_time_autocomplete,
)
from bot.apps.bot_messages.embeds import SendMessageByBotEmbed
from bot.apps.bot_messages.exceptions import BotMessageError
from bot.apps.bot_messages.modals import SendMessageByBotModal
from bot.apps.bot_messages.services import DelayedMessageService
from bot.config import logger


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
        self.check_delayed_messages.start()

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
        send_time = parse_complete_time(send_time)
        await ctx.send_modal(
            SendMessageByBotModal(
                delayed_message_service=self.delayed_message_service,
                send_time=send_time,
                title='',
                text_before=text_before,
            )
        )

    @message_group.command(description='Очистить очередь отложенных сообщений')
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
            embed = SendMessageByBotEmbed.build(
                content=message.embed_content,
                image_url=message.image_url,
            )
            channel = await self.bot.fetch_channel(message.channel_id)
            await channel.send(content=message.before_text, embeds=[embed])

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: BotMessageError):
        if isinstance(error, BotMessageError):
            return await ctx.respond(error.message, ephemeral=True)
        raise error

    def cog_unload(self) -> None:
        self.check_delayed_messages.cancel()
