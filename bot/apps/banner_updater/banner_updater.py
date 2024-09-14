from io import BytesIO
from typing import TYPE_CHECKING

from discord import File, NoMoreItems, TextChannel
from discord.ext import commands, tasks

from bot.apps.server_status.exceptions import LastMessageAuthorIsNotSelfError
from bot.apps.server_status.views import FindServerView
from bot.config import settings
from bot.dynamic_settings import dynamic_settings
from core.clients.redis import RedisNameSpace
from core.localization import LocaleEnum
from core.logger import logger
from global_constants import IMAGES_NAMESPACE, DISCOR_BANNER_IMAGE_KEY

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
