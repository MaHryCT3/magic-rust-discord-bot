from discord import Member, VoiceChannel, VoiceState
from discord.ext import commands, tasks

from bot.bot import MagicRustBot
from bot.dynamic_settings import dynamic_settings
from core.utils.decorators import loop_stability_checker, suppress_exceptions

SERVER_DELETE_UPDATE_SECONDS = 60.0


class RoomCleaner(commands.Cog):
    def __init__(self, bot: MagicRustBot):
        self.bot = bot

    def cog_unload(self):
        self.delete_empty_channels.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.delete_empty_channels.start()

    @commands.Cog.listener()
    async def on_voice_state_update(self, _member: Member, before: VoiceState, _after: VoiceState):
        if not before.channel:
            return
        if self._is_channel_room_and_empty(before.channel):
            await before.channel.delete()

    @tasks.loop(seconds=SERVER_DELETE_UPDATE_SECONDS)
    @loop_stability_checker(seconds=SERVER_DELETE_UPDATE_SECONDS)
    @suppress_exceptions
    async def delete_empty_channels(self):
        guild = self.bot.get_main_guild()

        channels_to_delete = [
            channel for channel in await guild.fetch_channels() if self._is_channel_room_and_empty(channel)
        ]
        for channel in channels_to_delete:
            await channel.delete()

    @staticmethod
    def _is_channel_room_and_empty(channel: VoiceChannel) -> bool:
        return (
            isinstance(channel, VoiceChannel)
            and not channel.voice_states
            and channel.category_id in dynamic_settings.user_rooms_categories.values()
        )
