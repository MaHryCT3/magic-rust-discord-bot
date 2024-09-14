from io import BytesIO
from typing import TYPE_CHECKING

from discord.ext import commands, tasks

from bot.config import settings
from core.clients.redis import RedisNameSpace
from core.logger import logger
from global_constants import DISCOR_BANNER_IMAGE_KEY, IMAGES_NAMESPACE

if TYPE_CHECKING:
    from bot import MagicRustBot

BANNER_UPDATE_SECONDS = 30.0


class BannerUpdater(commands.Cog):
    def __init__(self, bot: 'MagicRustBot'):
        self.bot = bot
        self.image_storage = RedisNameSpace(settings.REDIS_URL, IMAGES_NAMESPACE)

    def cog_unload(self):
        self.update_server_status.cancel()

    @tasks.loop(seconds=BANNER_UPDATE_SECONDS)
    async def update_server_status(self):
        image_bytes: bytes = self.image_storage.get(DISCOR_BANNER_IMAGE_KEY, as_bytes=True)
        if not image_bytes:
            logger.warning('Header image not loaded')
        else:
            guild = self.bot.get_main_guild()
            # image_binary = BytesIO(image_bytes)
            with BytesIO(image_bytes) as image_binary:
                await guild.edit(banner=image_binary)
