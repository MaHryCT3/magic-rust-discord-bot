from typing import Any, NoReturn

import discord
from discord.bot import Bot

from reports.config import logger, settings
from reports.exceptions import ReportsError

COGS = [
    'setup',
]


class MagicRustReportBot(Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        super().__init__(
            *args,
            intents=intents,
            owner_ids=settings.DISCORD_OWNER_IDS,
            **kwargs,
        )
        self._load_cogs()

    def _load_cogs(self):
        for cog in COGS:
            cog_with_path = 'reports.' + cog
            self.load_extension(cog_with_path)
            logger.info(f'Cog {cog_with_path} is loaded')

    async def on_application_command_error(self, ctx: discord.ApplicationContext, exception: discord.DiscordException):
        if isinstance(exception, ReportsError):
            return await ctx.respond(exception.message, ephemeral=True, delete_after=20)
        return await super().on_application_command_error(ctx, exception)

    def run(self, *args: Any, **kwargs: Any) -> NoReturn:
        super().run(settings.DISCORD_REPORT_BOT_TOKEN, *args, **kwargs)

    async def on_ready(self):
        logger.info('Bot is running')
