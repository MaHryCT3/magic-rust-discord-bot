import datetime
from dataclasses import dataclass

import discord

from bot.apps.exporter.actions.export_chats import ExportChatAction
from bot.apps.exporter.actions.export_forums import ExportForumAction
from bot.apps.exporter.actions.make_file_exported_messages import MakeExportFile
from core.actions.abstract import AbstractAction


@dataclass
class ExportChatsPipeline(AbstractAction):
    date_from: datetime.datetime
    date_to: datetime.datetime
    channels: list[discord.ForumChannel | discord.TextChannel] | None = None

    @property
    def text_channels(self) -> list[discord.TextChannel] | None:
        return (
            [channel for channel in self.channels if isinstance(channel, discord.TextChannel)]
            if self.channels
            else None
        )

    @property
    def forum_channels(self) -> list[discord.ForumChannel] | None:
        return (
            [channel for channel in self.channels if isinstance(channel, discord.ForumChannel)]
            if self.channels
            else None
        )

    @property
    def filename_template(self) -> str:
        return 'exported_{}_{}-{}.json'.format(
            '{}',
            self.date_from.strftime('%d_%m_%Y'),
            self.date_to.strftime('%d_%m_%y'),
        )

    async def action(self) -> list[discord.File]:
        exported_chats = await self._export_text_chats()
        exported_forums = await self._export_forums()

        exported_files = []
        exported_files.extend(await self._get_chat_files(exported_chats))
        exported_files.extend(await self._get_forum_files(exported_forums))

        return exported_files

    async def _export_text_chats(self) -> dict[discord.TextChannel, list[discord.Message]]:
        exported_chats = {}
        for channel in self.text_channels:
            exported_chats[channel] = await ExportChatAction(
                self.date_from,
                self.date_to,
                channel=channel,
            ).execute()
        return exported_chats

    async def _export_forums(self) -> dict[discord.ForumChannel, dict[discord.Thread, list[discord.Message]]]:
        exported_forums = {}
        for forum in self.forum_channels:
            exported_forums[forum] = await ExportForumAction(
                self.date_from,
                self.date_to,
                forum=forum,
            ).execute()
        return exported_forums

    async def _get_chat_files(
        self, export_chats: dict[discord.TextChannel, list[discord.Message]]
    ) -> list[discord.File]:
        files = []
        for chat, messages in export_chats.items():
            files.append(
                await MakeExportFile(
                    {chat: messages},
                    file_name=self.filename_template.format(chat.name),
                ).execute()
            )
        return files

    async def _get_forum_files(
        self, exported_forums: dict[discord.ForumChannel, dict[discord.Thread, list[discord.Message]]]
    ) -> list[discord.File]:
        files = []
        for forum, threads_with_messages in exported_forums.items():
            files.append(
                await MakeExportFile(
                    threads_with_messages,
                    file_name=self.filename_template.format(forum.name),
                ).execute()
            )
        return files
