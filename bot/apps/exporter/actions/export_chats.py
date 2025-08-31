import datetime
from dataclasses import dataclass

import discord

from bot.dynamic_settings import dynamic_settings
from core.actions.abstract import AbstractAction
from core.shortcuts import get_or_fetch_channel


@dataclass
class ExportChatsAction(AbstractAction[dict[discord.TextChannel, list[discord.Message]]]):
    guild: discord.Guild
    date_from: datetime.datetime
    date_to: datetime.datetime
    channels: list[discord.TextChannel] | None = None

    async def action(self) -> dict[discord.TextChannel | discord.ForumChannel, list[discord.Message]]:
        channels = self.channels or await self._get_default_export_channels()

        result: dict[discord.TextChannel, list[discord.Message]] = {}
        for channel in channels:
            channel_messages = await self._get_channel_message(channel)

            result[channel] = channel_messages
        return result

    async def _get_default_export_channels(self) -> list[discord.TextChannel | discord.ForumChannel]:
        channels = [
            await get_or_fetch_channel(self.guild, channel_id)
            for channel_id in dynamic_settings.default_export_channels
        ]
        return [channel for channel in channels if isinstance(channel, discord.TextChannel)]

    async def _get_channel_message(self, channel: discord.TextChannel | discord.ForumChannel) -> list[discord.Message]:
        chanel_message = [
            message
            async for message in channel.history(
                before=self.date_to,
                after=self.date_from,
                oldest_first=True,
            )
        ]
        return chanel_message
