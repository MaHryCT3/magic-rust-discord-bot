from io import BytesIO
from time import time
from typing import TYPE_CHECKING

from discord import File, NoMoreItems, TextChannel
from discord.ext import commands, tasks

from bot.apps.image_updater.exceptions import LastMessageAuthorIsNotSelfError
from bot.config import logger, settings
from bot.dynamic_settings import dynamic_settings
from core.clients.redis import RedisNameSpace
from global_constants import SERVER_STATUS_IMAGE_KEY

if TYPE_CHECKING:
    from bot import MagicRustBot

HEADER_UPDATE_SECONDS = 30.0
SERVER_STATUS_UPDATE_SECONDS = 15.0


class ImageUpdater(commands.Cog):
    def __init__(self, bot: 'MagicRustBot'):
        self.bot = bot
        self.image_storage = RedisNameSpace(settings.REDIS_URL, 'images')
        self.update_server_status.start()
        self.last_time = time()

    def cog_unload(self):
        self.update_server_status.cancel()

    @tasks.loop(seconds=SERVER_STATUS_UPDATE_SECONDS)
    async def update_server_status(self):
        channel_id = dynamic_settings.server_status_channel
        if not channel_id:
            return
        channel: TextChannel = await self.bot.fetch_channel(channel_id)
        try:
            last_message = await channel.history().next()
        except NoMoreItems:
            last_message = None
        if last_message and not last_message.author.bot:
            raise LastMessageAuthorIsNotSelfError('Last message should have been sent by bot, not user.')
        image_bytes: bytes = self.image_storage.get(SERVER_STATUS_IMAGE_KEY, as_bytes=True)

        if not image_bytes:
            logger.warn('image not loaded')
        else:
            image_binary = BytesIO(image_bytes)
            if not last_message:
                await channel.send(file=File(image_binary, filename='server_status.png'))
            else:
                await last_message.edit(file=File(image_binary, filename='server_status.png'), attachments=[])
            image_binary.close()
