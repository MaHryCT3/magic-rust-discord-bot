from dataclasses import dataclass

import discord

from core.actions.abstract import AbstractAction


@dataclass
class SetRoomLimitAction(AbstractAction):
    voice_channel: discord.VoiceChannel
    limit: int

    async def action(self):
        await self.voice_channel.edit(user_limit=self.limit)
