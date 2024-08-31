from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from bot.dynamic_settings import dynamic_settings
from bot.exceptions import ChannelNotConfiguredError

if TYPE_CHECKING:
    from bot import MagicRustBot


class ImageUpdaterCommands(commands.Cog):
    def __init__(self, bot: 'MagicRustBot') -> None:
        self.bot = bot

    @commands.slash_command(
        description='Отправить стартовые сообщения в канал статуса серверов',
        contexts={discord.InteractionContextType.guild},
    )
    async def initialize_server_status_channel(self, ctx: discord.ApplicationContext) -> None:
        channel_id = dynamic_settings.server_status_channel
        if not channel_id:
            raise ChannelNotConfiguredError('Server status channel is not set')
        print(type(channel_id))
        channel: discord.TextChannel = await self.bot.fetch_channel(channel_id)
        await ctx.respond(f"Сообщеия отправлены в канал {channel.name}", ephemeral=True)