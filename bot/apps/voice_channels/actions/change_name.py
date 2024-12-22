from dataclasses import dataclass

import discord

from core.actions.abstract import AbstractAction


@dataclass
class ChangeNameAction(AbstractAction):
    voice_channel: discord.VoiceChannel
    new_name: str

    async def action(self):
        await self.voice_channel.edit(name=self.new_name)
