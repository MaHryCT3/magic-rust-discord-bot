from typing import Any, NoReturn

import discord
from discord.bot import Bot

from bot.config import settings
from bot.dynamic_settings import CategoryId, dynamic_settings
from core.localization import LocaleEnum
from core.logger import logger

all_apps = [
    'find_friends',
    'settings',
    'bot_messages',
    'info_provider',
    'server_status',
    'banner_updater',
    'voice_channels',
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

    def get_category(self, category_id: CategoryId) -> discord.CategoryChannel | None:
        for category in self.get_main_guild().categories:
            if category.id == category_id:
                return category
        return None

    def get_locale_role(self, locale: LocaleEnum):
        for role_id, role_locale in dynamic_settings.locale_roles.items():
            if locale == role_locale:
                return self.get_main_guild().get_role(role_id)

    async def fetch_main_guild(self) -> discord.Guild:
        return await self.fetch_guild(settings.MAGIC_RUST_GUILD_ID, with_counts=True)

    async def on_ready(self):
        logger.info('Bot is running')

    def run(self, *args: Any, **kwargs: Any) -> NoReturn:
        super().run(settings.DISCORD_MAIN_BOT_TOKEN, *args, **kwargs)
