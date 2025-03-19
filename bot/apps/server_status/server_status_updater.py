from io import BytesIO
from typing import TYPE_CHECKING

from discord import File, NoMoreItems, TextChannel
from discord.ext import commands, tasks

from bot.apps.server_status.exceptions import LastMessageAuthorIsNotSelfError
from bot.apps.server_status.views import FindServerView
from bot.config import settings
from bot.dynamic_settings import dynamic_settings
from core.clients.async_redis import AsyncRedisNameSpace
from core.localization import LocaleEnum
from core.logger import logger
from core.utils.decorators import suppress_exceptions
from global_constants import IMAGES_NAMESPACE, SERVER_STATUS_IMAGE_KEY

if TYPE_CHECKING:
    from bot import MagicRustBot

SERVER_STATUS_UPDATE_SECONDS = 15.0


class ServerStatusUpdater(commands.Cog):
    def __init__(self, bot: 'MagicRustBot'):
        self.bot = bot
        self.image_storage = AsyncRedisNameSpace(settings.REDIS_URL, IMAGES_NAMESPACE)

    def cog_unload(self):
        self.update_server_status.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.filter_view_localization: dict[LocaleEnum, FindServerView] = FindServerView.get_localized_views()
        for send_filter_view in self.filter_view_localization.values():
            self.bot.add_view(send_filter_view)
        self.update_server_status.start()

    @tasks.loop(seconds=SERVER_STATUS_UPDATE_SECONDS)
    @suppress_exceptions
    async def update_server_status(self):
        for locale, channel_id in dynamic_settings.server_status_channels.items():
            channel: TextChannel = await self.bot.fetch_channel(channel_id)
            try:
                last_message = await channel.history().next()
            except NoMoreItems:
                last_message = None
            if last_message and not last_message.author.bot:
                raise LastMessageAuthorIsNotSelfError('Last message should have been sent by bot, not user.')
            image_bytes: bytes = await self.image_storage.get(SERVER_STATUS_IMAGE_KEY, as_bytes=True)

            if not image_bytes:
                logger.warning('Server status image not loaded')
            else:
                image_binary = BytesIO(image_bytes)

                file = File(image_binary, filename='server_status.png')
                if not last_message:
                    await channel.send(
                        file=file,
                        view=self.filter_view_localization[locale],
                    )
                else:
                    await last_message.edit(
                        file=file,
                        attachments=[],
                    )
                image_binary.close()


#
