from typing import Any, NoReturn

from discord.bot import Bot
from bot.config import logger, settings


class MagicRustBot(Bot):
    async def on_ready(self):
        logger.info('Bot is running')

    def run(self, *args: Any, **kwargs: Any) -> NoReturn:
        super().run(settings.DISCORD_BOT_TOKEN, *args, **kwargs)


