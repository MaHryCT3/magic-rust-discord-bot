from dataclasses import dataclass

import discord

from bot.apps.voice_channels.permissions import (
    creator_room_permission,
    member_room_permission,
)
from core.actions.abstract import AbstractAction


@dataclass
class TransferRightsAction(AbstractAction):
    voice_channel: discord.VoiceChannel
    member: discord.Member
    initiator: discord.Member

    async def action(self) -> None:
        await self.voice_channel.edit(
            overwrites={
                self.member: creator_room_permission,
                self.initiator: member_room_permission,
            }
        )
