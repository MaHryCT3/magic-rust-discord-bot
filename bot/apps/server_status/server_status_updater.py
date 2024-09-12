from io import BytesIO
from typing import TYPE_CHECKING

from discord import File, NoMoreItems, TextChannel
from discord.ext import commands, tasks

from bot.apps.server_status.exceptions import LastMessageAuthorIsNotSelfError
from bot.apps.server_status.views import FindServerView
from bot.config import logger, settings
from bot.dynamic_settings import dynamic_settings
from core.clients.redis import RedisNameSpace
from core.localization import LocaleEnum
from global_constants import IMAGES_NAMESPACE, SERVER_STATUS_IMAGE_KEY

if TYPE_CHECKING:
    from bot import MagicRustBot

HEADER_UPDATE_SECONDS = 30.0
SERVER_STATUS_UPDATE_SECONDS = 15.0


class ServerStatusUpdater(commands.Cog):
    def __init__(self, bot: 'MagicRustBot'):
        self.bot = bot
        self.image_storage = RedisNameSpace(settings.REDIS_URL, IMAGES_NAMESPACE)

    def cog_unload(self):
        self.update_server_status.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.filter_view_localization: dict[LocaleEnum, FindServerView] = FindServerView.get_localized_views()
        for send_filter_view in self.filter_view_localization.values():
            self.bot.add_view(send_filter_view)
        self.update_server_status.start()

    @tasks.loop(seconds=SERVER_STATUS_UPDATE_SECONDS)
    async def update_server_status(self):
        for locale, channel_id in dynamic_settings.server_status_channels.items():
            channel: TextChannel = await self.bot.fetch_channel(channel_id)
            try:
                last_message = await channel.history().next()
            except NoMoreItems:
                last_message = None
            if last_message and not last_message.author.bot:
                raise LastMessageAuthorIsNotSelfError('Last message should have been sent by bot, not user.')
            image_bytes: bytes = self.image_storage.get(SERVER_STATUS_IMAGE_KEY, as_bytes=True)

            if not image_bytes:
                logger.warning('image not loaded')
            else:
                image_binary = BytesIO(image_bytes)
                if not last_message or not last_message.attachments:
                    await channel.send(
                        file=File(image_binary, filename='server_status.png'),
                        view=self.filter_view_localization[locale],
                    )
                else:
                    await last_message.edit(file=File(image_binary, filename='server_status.png'), attachments=[])
                image_binary.close()
