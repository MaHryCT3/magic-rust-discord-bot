from discord import VoiceChannel
from discord.ext import commands, tasks

from bot.bot import MagicRustBot
from bot.config import settings
from bot.dynamic_settings import ChannelId, dynamic_settings
from core.clients.redis import RedisNameSpace
from core.localization import LocaleEnum
from global_constants import TEMPORARY_CHANNELS_KEY, VOICE_CHANNELS_NAMESPACE

CREATE_SERVER_UPDATE_SECONDS = 0.5
SERVER_DELETE_UPDATE_SECONDS = 2.0


# TODO: add channel groups support
class ChannelCleaner(commands.Cog):
    def __init__(self, bot: MagicRustBot):
        self.bot = bot
        self.channels_storage = RedisNameSpace(settings.REDIS_URL, VOICE_CHANNELS_NAMESPACE)

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_creating_channels.start()
        self.delete_empty_channels.start()

    @tasks.loop(seconds=CREATE_SERVER_UPDATE_SECONDS)
    async def check_creating_channels(self):
        for locale, channel_id in dynamic_settings.channel_creating_channels.items():
            channel: VoiceChannel = await self.bot.fetch_channel(channel_id)
            for member in channel.members:
                new_channel = await self.create_temporary_channel(locale)
                await member.move_to(new_channel)

    @tasks.loop(seconds=SERVER_DELETE_UPDATE_SECONDS)
    async def delete_empty_channels(self):
        temporary_channels_ids = self.get_temporary_channels()
        for channel_id in temporary_channels_ids:
            channel: VoiceChannel = await self.bot.fetch_channel(channel_id)
            print(channel)
            if len(channel.members) == 0:
                self.remove_temporary_channel_id(channel.id)
                await channel.delete()

    def get_temporary_channels(self) -> list[ChannelId]:
        temporary_channels_str: str = self.channels_storage.get(TEMPORARY_CHANNELS_KEY)
        if not temporary_channels_str:
            return []
        temporary_channels = temporary_channels_str.split(' ')
        print(temporary_channels)
        return [int(channel_id) for channel_id in temporary_channels]

    def set_temporary_channels(self, value: list[str]):
        self.channels_storage.set(TEMPORARY_CHANNELS_KEY, ' '.join(value))

    def save_temporary_channel_id(self, channel_id):
        temporary_channels = self.get_temporary_channels()
        temporary_channels.append(str(channel_id))
        self.set_temporary_channels(temporary_channels)

    def remove_temporary_channel_id(self, channel_id):
        temporary_channels = self.get_temporary_channels()
        temporary_channels.remove(channel_id)
        self.set_temporary_channels(temporary_channels)

    async def create_temporary_channel(self, locale: LocaleEnum) -> VoiceChannel:
        guild = self.bot.get_main_guild()
        new_channel = await guild.create_voice_channel(
            'Name for channel' if locale == LocaleEnum.en else 'Пидорасы снизу ↓'
        )
        self.save_temporary_channel_id(new_channel.id)
        return new_channel
