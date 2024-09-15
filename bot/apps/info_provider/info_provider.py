from discord.ext import commands, tasks

from bot import MagicRustBot
from bot.config import settings
from core.clients.redis import RedisNameSpace
from core.utils.decorators import suppress_exceptions
from global_constants import (
    DISCORD_INFO_NAMESPACE,
    DISCORD_ONLINE_PRESENCE_KEY,
    DISCORD_VOICE_PRESENCE_KEY,
)

INFO_EXPIRATION_TIME = 600
REPEAT_SECONDS = 10.0


class InfoProvider(commands.Cog):
    def __init__(self, bot: 'MagicRustBot'):
        self.bot = bot
        self.info_storage = RedisNameSpace(settings.REDIS_URL, namespace=DISCORD_INFO_NAMESPACE)
        self.provide_info.start()

    def cog_unload(self):
        self.provide_info.cancel()

    @tasks.loop(seconds=REPEAT_SECONDS)
    @suppress_exceptions
    async def provide_info(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_main_guild()
        fetched_guild = await self.bot.fetch_main_guild()
        online_presence = fetched_guild.approximate_presence_count
        voice_presence = sum([len(voice_channel.members) for voice_channel in guild.voice_channels])
        self.info_storage.set(DISCORD_ONLINE_PRESENCE_KEY, online_presence, INFO_EXPIRATION_TIME)
        self.info_storage.set(DISCORD_VOICE_PRESENCE_KEY, voice_presence, INFO_EXPIRATION_TIME)
