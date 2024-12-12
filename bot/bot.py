from typing import Any, NoReturn

import discord
import sentry_sdk
from discord import ApplicationContext, CheckFailure, DiscordException
from discord.bot import Bot

from bot.apps.users.utils import get_member_locale
from bot.config import settings
from bot.dynamic_settings import CategoryId, dynamic_settings
from core.localization import LocaleEnum
from core.logger import logger

all_apps = [
    'auto_moderation',
    'find_friends',
    'settings',
    'bot_messages',
    'info_provider',
    'server_status',
    'banner_updater',
    'voice_channels',
    'news_reposts',
    'reports',
    'tickets',
    'unban_tickets',
    'users',
    'servicing_posts',
]


class MagicRustBot(Bot):
    def __init__(self, *args, setup_apps: list[str] | None = None, **kwargs):
        self.setup_apps = setup_apps or all_apps
        intents = discord.Intents.default() + discord.Intents.message_content + discord.Intents.members
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

    def get_category(self, category_id: CategoryId) -> discord.CategoryChannel | None:
        for category in self.get_main_guild().categories:
            if category.id == category_id:
                return category
        return None

    def get_locale_role(self, locale: LocaleEnum) -> discord.Role:
        role_id = dynamic_settings.locale_roles[locale]
        return self.get_main_guild().get_role(role_id)

    def get_main_guild(self) -> discord.Guild | None:
        return self.get_guild(int(settings.MAGIC_RUST_GUILD_ID))

    async def fetch_main_guild(self, with_count: bool = True) -> discord.Guild:
        return await self.fetch_guild(settings.MAGIC_RUST_GUILD_ID, with_counts=with_count)

    async def get_or_fetch_main_guild(self) -> discord.Guild:
        if guild := self.get_main_guild():
            return guild
        return await self.fetch_main_guild(with_count=False)

    async def on_application_command_error(self, context: ApplicationContext, exception: DiscordException) -> None:
        if isinstance(exception, CheckFailure):
            locale = get_member_locale(context.user) or LocaleEnum.ru
            error_map = {
                LocaleEnum.en: "You can't use this command😞",
                LocaleEnum.ru: 'Вы не можете использовать эту команду😞',
            }
            await context.respond(
                error_map[locale],
                ephemeral=True,
                delete_after=20,
            )
            return

        await super().on_application_command_error(context, exception)
        sentry_sdk.capture_exception(exception)

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        sentry_sdk.capture_exception()
        return await super().on_error(event_method, *args, **kwargs)

    async def on_ready(self):
        info = await self.application_info()
        logger.info(f'Bot {info.name} is running')

    def run(self, *args: Any, **kwargs: Any) -> NoReturn:
        super().run(settings.DISCORD_BOT_TOKEN, *args, **kwargs)
