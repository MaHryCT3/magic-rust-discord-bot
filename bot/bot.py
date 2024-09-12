from typing import Any, NoReturn

import discord
from discord.bot import Bot

from bot.config import logger, settings
from bot.dynamic_settings import CategoryId

COGS = [
    # 'apps.find_friends.setup',
    # 'apps.settings.setup',
    # 'apps.bot_messages.setup',
    # 'apps.info_provider.setup',
    # 'apps.server_status.setup',
    # 'apps.news_reposts.setup',
    'apps.channel_cleaner.setup',
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

    def get_main_guild(self) -> discord.Guild | None:
        return self.get_guild(int(settings.MAGIC_RUST_GUILD_ID))

    def get_category(self, category_id: CategoryId) -> discord.CategoryChannel | None:
        for category in self.get_main_guild().categories:
            if category.id == category_id:
                return category
        return None

    async def fetch_main_guild(self) -> discord.Guild:
        return await self.fetch_guild(settings.MAGIC_RUST_GUILD_ID, with_counts=True)

    async def on_ready(self):
        logger.info('Bot is running')

    def run(self, *args: Any, **kwargs: Any) -> NoReturn:
        super().run(settings.DISCORD_MAIN_BOT_TOKEN, *args, **kwargs)
