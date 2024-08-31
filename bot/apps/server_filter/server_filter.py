from typing import TYPE_CHECKING

from discord.ext import commands

from bot.config import logger
from bot.dynamic_settings import dynamic_settings
from core.localization import LocaleEnum

if TYPE_CHECKING:
    from bot import MagicRustBot


class ServerFilter(commands.Cog):
    def __init__(self, bot: 'MagicRustBot'):
        self.bot = bot