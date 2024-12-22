from dataclasses import dataclass

import discord

from core.actions.abstract import AbstractAction


@dataclass
class KickMemberAction(AbstractAction):
    voice_channel: discord.VoiceChannel
    member: discord.Member

    async def action(self) -> None:
        permissions = discord.PermissionOverwrite()
        permissions.connect = False
        await self.voice_channel.set_permissions(self.member, overwrite=permissions)
        await self.member.move_to(None)
