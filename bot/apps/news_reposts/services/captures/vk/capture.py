import io

import aiohttp
import discord

from bot.apps.news_reposts.constants import DEFAULT_POLL_DURATION_IN_HOURS
from bot.apps.news_reposts.services.captures.abc import AbstractNewsCapture
from bot.apps.news_reposts.services.captures.structs import (
    URL,
    CapturedNews,
    CapturedNewsSources,
)
from core.api_clients.vk import BotPolling, UpdateTypes
from core.api_clients.vk.models import (
    DocAttachment,
    PhotoAttachment,
    PollAttachment,
    VideoAttachment,
    WallPost,
)
from core.api_clients.vk.models.wall_post import PostTypeEnum
from core.api_clients.vk.utils import make_url_to_vk_post
from core.converters import seconds_to_hours


class VKNewsCapture(AbstractNewsCapture):

    def __init__(self, bot_polling: BotPolling):
        self.bot_polling = bot_polling

    async def get_captured_news(self) -> list[CapturedNews]:
        new_posts: list[WallPost] = await self.bot_polling.get_new_events(
            update_types=[UpdateTypes.WALL_POST_NEW], parse_response=True
        )
        if not new_posts:
            return []

        captured_news = []
        for post in new_posts:
            if post.post_type != PostTypeEnum.POST:
                continue

            images_urls = self._get_images_urls(post)
            files = await self._get_files(post)
            poll = self._get_poll(post)
            captured_news.append(
                CapturedNews(
                    text=post.text,
                    images=images_urls,
                    files=files,
                    poll=poll,
                    source=CapturedNewsSources.VK,
                    original_link=make_url_to_vk_post(post.group_id, post.id),
                )
            )
        return captured_news

    @staticmethod
    def _get_images_urls(wall_post: WallPost) -> list[URL]:
        urls = []
        for attachment in wall_post.attachments:
            if isinstance(attachment, PhotoAttachment):
                urls.append(attachment.orig_photo.url)
            elif isinstance(attachment, VideoAttachment):
                urls.append(attachment.image[-1].url)
        return list(urls)

    async def _get_files(self, wall_post: WallPost) -> list[discord.File]:
        files: list[discord.File] = []
        for attachment in wall_post.attachments:
            if not isinstance(attachment, DocAttachment):
                continue

            file = await self._get_files_bytes(attachment.url, attachment.title)
            files.append(file)

        return files

    @staticmethod
    async def _get_files_bytes(url: str, filename: str) -> discord.File:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                file = await response.read()
                with io.BytesIO(file) as file_bytes:
                    return discord.File(file_bytes, filename=filename)

    @staticmethod
    def _get_poll(post: WallPost) -> discord.Poll | None:
        for attachment in post.attachments:
            if isinstance(attachment, PollAttachment):
                poll = attachment
                break
        else:
            return

        return discord.Poll(
            allow_multiselect=poll.multiple,
            question=poll.question,
            answers=[discord.PollAnswer(text=answer) for answer in poll.answers],
            duration=(
                seconds_to_hours(poll.end_date - poll.created) if poll.end_date else DEFAULT_POLL_DURATION_IN_HOURS
            ),
        )
