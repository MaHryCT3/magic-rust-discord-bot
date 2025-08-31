import datetime
from dataclasses import dataclass

import discord

from bot.dynamic_settings import dynamic_settings
from core.actions.abstract import AbstractAction
from core.shortcuts import get_or_fetch_channel


@dataclass
class ExportForumsAction(AbstractAction[dict[discord.Thread, list[discord.Message]]]):
    guild: discord.Guild
    date_from: datetime.datetime
    date_to: datetime.datetime
    channels: list[discord.ForumChannel] | None = None

    async def action(self) -> dict[discord.Thread, list[discord.Message]]:
        channels = self.channels or await self._get_default_export_channels()

        result: dict[discord.Thread, list[discord.Message]] = {}
        for channel in channels:
            threads = await self._get_channel_threads(channel)
            for thread in threads:
                result[thread] = await self._get_threads_export_messages(thread)
        return result

    async def _get_default_export_channels(self) -> list[discord.ForumChannel]:
        channels = [
            await get_or_fetch_channel(self.guild, channel_id)
            for channel_id in dynamic_settings.default_export_channels
        ]
        return [channel for channel in channels if isinstance(channel, discord.ForumChannel)]

    async def _get_channel_threads(self, channel: discord.ForumChannel) -> list[discord.Thread]:
        archived_threads = []
        async for thread in channel.archived_threads(limit=None):
            archived_threads.append(thread)

            if not self._is_thread_fit(thread):
                break

        threads: list[discord.Thread] = [thread for thread in channel.threads if await self._is_thread_fit(thread)]
        return threads + archived_threads

    async def _get_threads_export_messages(self, thread: discord.Thread) -> list[discord.Message]:
        return [
            message
            async for message in thread.history(
                oldest_first=True,
                limit=None,
            )
        ]

    async def _is_thread_fit(self, thread: discord.Thread) -> bool:
        last_message = thread.last_message
        if not last_message:
            history = thread.history(limit=1)
            try:
                last_message = await anext(history)
            except StopAsyncIteration:
                last_message = None

        if last_message:
            date_checking = last_message.created_at
        else:
            date_checking = thread.created_at

        return self.date_from <= date_checking <= self.date_to
