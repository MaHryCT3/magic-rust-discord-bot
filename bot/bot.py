from typing import Any, NoReturn

import discord
from discord.bot import Bot

from bot.config import logger, settings

COGS = [
    'apps.find_friends.setup',
    'apps.settings.setup',
    'apps.bot_messages.setup',
]


class MagicRustBot(Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default() + discord.Intents.message_content
        super().__init__(*args, intents=intents, **kwargs)
        self._load_cogs()

    def _load_cogs(self):
        for cog in COGS:
            cog_with_path = 'bot.' + cog
            self.load_extension(cog_with_path)
            logger.info(f'Cog {cog_with_path} is loaded')

    async def on_ready(self):
        logger.info('Bot is running')

    async def on_connect(self):
        await self.sync_commands()

    def run(self, *args: Any, **kwargs: Any) -> NoReturn:
        super().run(settings.DISCORD_BOT_TOKEN, *args, **kwargs)
