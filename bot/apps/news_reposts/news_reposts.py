import discord
from discord.ext import commands, tasks

from bot import MagicRustBot
from bot.apps.news_reposts.services.captures import (
    AbstractNewsCapture,
    CapturedNews,
    VKNewsCapture,
)
from bot.apps.news_reposts.services.captures.structs import CapturedNewsSources
from bot.apps.news_reposts.views import PreviewView
from bot.config import settings
from bot.dynamic_settings import dynamic_settings
from core.api_clients.vk import BotPolling, VKAPIClient
from core.logger import logger
from core.utils.decorators import suppress_exceptions
from global_constants import MAGIC_RUST_IMAGE

COLOR_BY_CAPTURE_SOURCE_MAP: dict[CapturedNewsSources, discord.Color] = {
    CapturedNewsSources.VK: discord.Color.blue(),
}


class NewsRepostsCog(commands.Cog):
    def __init__(self, bot: MagicRustBot):
        self.bot = bot
        self.captures: list[AbstractNewsCapture] = [
            self._get_main_vk_group_capture(),
        ]
        self.repost_news.start()

    def cog_unload(self) -> None:
        self.repost_news.stop()

    @tasks.loop(seconds=10)
    @suppress_exceptions
    async def repost_news(self):
        logger.info('checking new news to send')
        for capture in self.captures:
            try:
                news = await capture.get_captured_news()
            except Exception as e:
                logger.error(f'Error when trying captured message by {capture}', exc_info=e)
                continue

            logger.info(f'new news for {capture.__class__.__name__}: {news}')
            for new in news:
                await self._send_captured_new(new)

    async def _send_captured_new(self, news: CapturedNews):
        embeds = self._build_news_embeds(news)
        channel: discord.TextChannel = await self.bot.fetch_channel(dynamic_settings.repost_preview_channel)

        content = news.original_link
        await channel.send(content=content, poll=news.poll, files=news.files, embeds=embeds, view=PreviewView(self.bot))

    @staticmethod
    def _build_news_embeds(news: CapturedNews) -> list[discord.Embed]:
        color = COLOR_BY_CAPTURE_SOURCE_MAP[news.source]
        main_embed = (
            discord.Embed(colour=color)
            .add_field(name='', value=news.text)
            .set_author(name='MAGIC RUST', icon_url=MAGIC_RUST_IMAGE)
        )
        if news.images:
            main_embed.set_image(url=news.images[0])

        image_embeds = []
        for image in news.images[1:]:
            image_embeds.append(discord.Embed(colour=color).set_image(url=image))

        return [main_embed] + image_embeds

    def _get_main_vk_group_capture(self) -> VKNewsCapture:
        api = VKAPIClient(token=settings.VK_MAIN_GROUP_TOKEN)
        polling = BotPolling(api=api, group_id=settings.VK_MAIN_GROUP_ID)
        return VKNewsCapture(polling)
