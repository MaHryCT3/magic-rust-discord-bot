import datetime
from dataclasses import dataclass

import discord

from core.actions.abstract import AbstractAction
from core.shortcuts import fetch_active_forum_threads


@dataclass
class ExportForumAction(AbstractAction[dict[discord.Thread, list[discord.Message]]]):
    date_from: datetime.datetime
    date_to: datetime.datetime
    forum: discord.ForumChannel

    async def action(self) -> dict[discord.Thread, list[discord.Message]]:
        result: dict[discord.Thread, list[discord.Message]] = {}
        threads = await self._get_channel_threads()
        for thread in threads:
            result[thread] = await self._get_threads_export_messages(thread)
        return result

    async def _get_channel_threads(self) -> list[discord.Thread]:
        archived_threads = []
        async for thread in self.forum.archived_threads(limit=None):
            if not await self._is_thread_fit(thread):
                break

            archived_threads.append(thread)

        threads: list[discord.Thread] = [
            thread for thread in await fetch_active_forum_threads(self.forum) if await self._is_thread_fit(thread)
        ]
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
