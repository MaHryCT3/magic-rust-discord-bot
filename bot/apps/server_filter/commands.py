from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from bot.apps.server_filter.embeds import ServerFilterGreetingEmbed
from bot.apps.server_filter.views import ServerFilterGreetingView
from bot.dynamic_settings import dynamic_settings
from bot.exceptions import ChannelNotConfiguredError
from core.localization import LocaleEnum

if TYPE_CHECKING:
    from bot import MagicRustBot


class ServerFilterCommands(commands.Cog):
    def __init__(self, bot: 'MagicRustBot') -> None:
        self.bot = bot
        
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.filter_view_localization: dict[LocaleEnum, ServerFilterGreetingView] = await ServerFilterGreetingView.get_localization_views()
        for send_filter_view in self.filter_view_localization.values():
            self.bot.add_view(send_filter_view)

    @commands.slash_command(
        description='Отправить стартовые сообщения в канал фильтра серверов',
        contexts={discord.InteractionContextType.guild},
    )
    async def initialize_server_filter_channel(self, ctx: discord.ApplicationContext) -> None:
        if not dynamic_settings.server_filter_channels:
            raise ChannelNotConfiguredError('Server filter channels are not set')
        channel_names = []
        for locale, channel_id in dynamic_settings.server_filter_channels.items():
            channel: discord.TextChannel = await self.bot.fetch_channel(channel_id)
            await channel.send(embed=ServerFilterGreetingEmbed.build(locale), view=self.filter_view_localization[locale])
            channel_names.append(channel.name)
        await ctx.respond(f"Сообщеия отправлены в канал(-ы) {", ".join(channel_names)}.", ephemeral=True)

