from typing import Any, NoReturn

import discord
from discord.bot import Bot

from bot.config import settings
from core.logger import logger

all_apps = [
    'find_friends',
    'settings',
    'bot_messages',
    'info_provider',
    'server_status',
    'news_reposts',
    'reports',
]


class MagicRustBot(Bot):
    def __init__(self, *args, setup_apps: list[str] | None = None, **kwargs):
        self.setup_apps = setup_apps or all_apps
        intents = discord.Intents.default() + discord.Intents.message_content
        super().__init__(
            *args,
            intents=intents,
            owner_ids=settings.DISCORD_OWNER_IDS,
            **kwargs,
        )
        self._load_apps()

    def _load_apps(self):
        for app_name in self.setup_apps:
            app_full_path = 'bot.apps.' + app_name + '.setup'
            self.load_extension(app_full_path)
            logger.info(f'app {app_full_path} is loaded')

    def get_main_guild(self) -> discord.Guild | None:
        return self.get_guild(int(settings.MAGIC_RUST_GUILD_ID))

    async def fetch_main_guild(self) -> discord.Guild:
        return await self.fetch_guild(settings.MAGIC_RUST_GUILD_ID, with_counts=True)

    async def on_ready(self):
        logger.info('Bot is running')

    def run(self, *args: Any, **kwargs: Any) -> NoReturn:
        super().run(settings.DISCORD_MAIN_BOT_TOKEN, *args, **kwargs)
