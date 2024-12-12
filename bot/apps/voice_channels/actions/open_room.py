from dataclasses import dataclass

import discord

from bot.apps.voice_channels.permissions import opened_room_permission
from bot.dynamic_settings import dynamic_settings
from core.actions.abstract import AbstractAction
from core.localization import LocaleEnum


@dataclass
class OpenRoomAction(AbstractAction):
    voice_channel: discord.VoiceChannel
    locale: LocaleEnum

    async def action(self):
        await self.voice_channel.set_permissions(
            target=self.voice_channel.guild.get_role(dynamic_settings.locale_roles[self.locale]),
            overwrite=opened_room_permission,
        )
