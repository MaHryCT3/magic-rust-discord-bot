from typing import TYPE_CHECKING

from discord.ext import commands, tasks

from bot.config import settings
from core.clients.async_redis import AsyncRedisNameSpace
from core.logger import logger
from core.utils.decorators import suppress_exceptions
from global_constants import DISCOR_BANNER_IMAGE_KEY, IMAGES_NAMESPACE

if TYPE_CHECKING:
    from bot import MagicRustBot

BANNER_UPDATE_SECONDS = 30.0


class BannerUpdater(commands.Cog):
    def __init__(self, bot: 'MagicRustBot'):
        self.bot = bot
        self.image_storage = AsyncRedisNameSpace(settings.REDIS_URL, IMAGES_NAMESPACE)

    def cog_unload(self):
        self.update_server_status.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_server_status.start()

    @tasks.loop(seconds=BANNER_UPDATE_SECONDS)
    @suppress_exceptions
    async def update_server_status(self):
        image_bytes: bytes = await self.image_storage.get(DISCOR_BANNER_IMAGE_KEY, as_bytes=True)
        if not image_bytes:
            logger.warning('Header image not loaded')
        else:
            guild = self.bot.get_main_guild()
            await guild.edit(banner=image_bytes)
