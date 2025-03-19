import dataclasses
import datetime

import discord
from discord import ChannelType

from bot.apps.voice_activity.services.activity_sender import ActivitySenderService
from bot.apps.voice_activity.structs.activity_message import ActivityMessage
from bot.apps.voice_activity.structs.enums import (
    ActivitySessionChannelType,
    ActivityStatus,
)
from bot.config import settings
from bot.dynamic_settings import dynamic_settings
from core.actions.abstract import AbstractAction


@dataclasses.dataclass
class SendActivityAction(AbstractAction):
    member: discord.Member
    voice_state: discord.VoiceState
    activity_status: ActivityStatus

    sender_service: ActivitySenderService = dataclasses.field(
        default_factory=ActivitySenderService,
    )

    @property
    def ignore_channel_ids(self):
        # Канал для создания каналов юзер находится меньше секунды, не имеет смысла записывать
        return dynamic_settings.channel_creating_channels.values()

    async def action(self):
        if self.voice_state.channel.id in self.ignore_channel_ids:
            return

        activity_message = ActivityMessage(
            datetime=datetime.datetime.now(tz=settings.TIMEZONE),
            user_id=str(self.member.id),
            channel_id=str(self.voice_state.channel.id),
            channel_type=self._get_channel_type(),
            activity_status=self.activity_status,
            is_sound_muted=self.voice_state.self_deaf or self.voice_state.deaf,
            is_microphone_muted=self.voice_state.self_mute or self.voice_state.mute,
        )
        await self.sender_service.send_activity(activity_message)

    def _get_channel_type(self) -> ActivitySessionChannelType:
        if self.voice_state.channel.type == ChannelType.stage_voice:
            return ActivitySessionChannelType.STAGE
        if self.voice_state.channel.category_id in dynamic_settings.user_rooms_categories.values():
            return ActivitySessionChannelType.USER_ROOM
        return ActivitySessionChannelType.VOICE
