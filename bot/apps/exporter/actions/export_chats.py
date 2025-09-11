import datetime
from dataclasses import dataclass

import discord

from core.actions.abstract import AbstractAction


@dataclass
class ExportChatAction(AbstractAction[dict[discord.TextChannel, list[discord.Message]]]):
    date_from: datetime.datetime
    date_to: datetime.datetime
    channel: discord.TextChannel

    async def action(self) -> list[discord.Message]:
        return await self._get_channel_message()

    async def _get_channel_message(self) -> list[discord.Message]:
        chanel_message = [
            message
            async for message in self.channel.history(
                before=self.date_to,
                after=self.date_from,
                limit=None,
                oldest_first=True,
            )
        ]
        return chanel_message
