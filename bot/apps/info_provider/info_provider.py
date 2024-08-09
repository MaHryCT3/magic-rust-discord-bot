from typing import TYPE_CHECKING

from discord.ext import tasks, commands
from core.clients.redis import RedisNameSpace
from bot.config import settings

if TYPE_CHECKING:
    from bot import MagicRustBot

INFO_EXPIRATION_TIME = 600
REPEAT_SECONDS = 10.0

class InfoProvider(commands.Cog):
    def __init__(self, bot: 'MagicRustBot'):
        self.bot = bot
        self.info_storage = RedisNameSpace(settings.REDIS_URL, 'discord_info')
        self.provide_info.start()

    def cog_unload(self):
        self.provide_info.cancel()
    
    @tasks.loop(seconds=REPEAT_SECONDS)
    async def provide_info(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_main_guild()
        fetched_guild = await self.bot.fetch_main_guild()
        online_presence = fetched_guild.approximate_presence_count
        voice_presence = sum([len(voice_channel.members) for voice_channel in guild.voice_channels])
        self.info_storage.set('online_presence', online_presence, INFO_EXPIRATION_TIME)
        self.info_storage.set('voice_presence', voice_presence, INFO_EXPIRATION_TIME)
        