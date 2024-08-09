from base64 import b64encode
from io import BytesIO
from typing import TYPE_CHECKING

from discord import Attachment, File, NotFound
from discord.ext import tasks, commands
from core.clients.redis import RedisNameSpace
from bot.config import settings
from bot.dynamic_settings import dynamic_settings
from core.localization import LocaleEnum
from time import time

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
        print(-self.last_time + time())
        self.last_time = time()
        # FIXME called more frequently than expected
        await self.bot.wait_until_ready()
        channel_id = dynamic_settings.server_status_channels.get(LocaleEnum('en-US'))
        if not channel_id:
            return
        channel = await self.bot.fetch_channel(channel_id)
        try:
            last_message = await channel.fetch_message(channel.last_message_id)
        except NotFound:
            last_message = None
        image_bytes: bytes = self.image_storage.get('server_status_image', as_bytes=True)
        
        if not image_bytes:
            print('image not loaded')
        else:
            image_binary = BytesIO(image_bytes)
            if not last_message:
                await channel.send(file=File(image_binary, filename='server_status.png'))
            else:
                await last_message.edit(file=File(image_binary, filename='server_status.png'), attachments=[])
            image_binary.close()