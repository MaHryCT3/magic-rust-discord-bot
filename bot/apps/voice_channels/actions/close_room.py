from dataclasses import dataclass

import discord

from bot.apps.voice_channels.permissions import (
    closed_room_permission,
    creator_room_permission,
)
from bot.dynamic_settings import dynamic_settings
from core.actions.abstract import AbstractAction
from core.localization import LocaleEnum


@dataclass
class CloseRoomAction(AbstractAction):
    voice_channel: discord.VoiceChannel
    locale: LocaleEnum

    async def action(self):
        members = (await self.voice_channel.guild.fetch_channel(self.voice_channel.id)).members
        members_managers = [member for member in members if self.voice_channel.permissions_for(member).manage_channels]
        managers_permissions = {member: creator_room_permission for member in members_managers}

        await self.voice_channel.edit(
            overwrites={
                **managers_permissions,
                self.voice_channel.guild.get_role(dynamic_settings.locale_roles[self.locale]): closed_room_permission,
            }
        )
