import datetime
from dataclasses import dataclass

import discord

from bot.apps.exporter.actions.export_chats import ExportChatsAction
from bot.apps.exporter.actions.export_forums import ExportForumsAction
from bot.apps.exporter.actions.make_file_exported_messages import MakeExportFile
from core.actions.abstract import AbstractAction


@dataclass
class ExportChatsPipeline(AbstractAction):
    guild: discord.Guild
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
        exported_chats = await ExportChatsAction(
            self.guild,
            self.date_from,
            self.date_to,
            self.text_channels,
        ).execute()
        exported_forums = await ExportForumsAction(
            self.guild,
            self.date_from,
            self.date_to,
            self.forum_channels,
        ).execute()

        exported_files = [
            await MakeExportFile(
                exported_chats,
                file_name=self.filename_template.format('chats'),
            ).execute(),
            await MakeExportFile(
                exported_forums,
                file_name=self.filename_template.format('forums'),
            ).execute(),
        ]

        return exported_files
