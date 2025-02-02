import discord
from discord.ext import tasks
from discord.ext.commands import Cog

from bot import MagicRustBot
from bot.apps.activity.actions.send_activity import SendActivityAction
from bot.apps.activity.services.activity_sender import ActivitySenderService
from bot.apps.activity.structs.enums import ActivityStatus
from core.shortcuts import get_or_fetch_member
from core.utils.decorators import suppress_exceptions


class ActivityProviderCog(Cog):
    def __init__(self, bot: MagicRustBot):
        self.bot = bot

        self._sender_service = ActivitySenderService()

        self._guild: discord.Guild = None

    def cog_unload(self):
        self._check_active_users.cancel()

    @Cog.listener()
    async def on_ready(self):
        self._guild = await self.bot.get_or_fetch_main_guild()
        self._check_active_users.start()

    @Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        if before.channel and before.channel != after.channel:
            await SendActivityAction(
                member=member,
                voice_state=before,
                activity_status=ActivityStatus.LEAVE,
            ).execute()

        if after.afk or after.channel is None:
            return

        if self._is_changed_or_joined_in_channel(before, after):
            await SendActivityAction(
                member=member,
                voice_state=after,
                activity_status=ActivityStatus.JOIN,
            ).execute()
        else:
            await SendActivityAction(
                member=member,
                voice_state=after,
                activity_status=ActivityStatus.ACTIVE,
            ).execute()

    @tasks.loop(seconds=60)
    @suppress_exceptions
    async def _check_active_users(self):
        for channel in await self._guild.fetch_channels():
            if not isinstance(channel, (discord.VoiceChannel, discord.StageChannel)):
                continue

            if not channel.voice_states:
                continue

            for member_id, voice_state in channel.voice_states.items():
                await SendActivityAction(
                    member=await get_or_fetch_member(self._guild, member_id),
                    voice_state=voice_state,
                    activity_status=ActivityStatus.ACTIVE,
                ).execute()

    @staticmethod
    def _is_changed_or_joined_in_channel(before: discord.VoiceState, after: discord.VoiceState) -> bool:
        if before.channel is None and after.channel:
            return True
        if before.channel != after.channel and after.channel:
            return True
        return False
