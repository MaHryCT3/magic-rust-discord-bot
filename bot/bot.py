from typing import Any, NoReturn

from discord.bot import Bot

from bot.config import logger, settings

COGS = [
    'find_friends.setup',
    'settings.setup',
]


class MagicRustBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._load_cogs()

    def _load_cogs(self):
        for cog in COGS:
            cog_with_path = 'bot.' + cog
            self.load_extension(cog_with_path)
            logger.info(f'Cog {cog_with_path} is loaded')

    async def on_ready(self):
        logger.info('Bot is running')

    async def on_connect(self):
        await self.sync_commands()

    def run(self, *args: Any, **kwargs: Any) -> NoReturn:
        super().run(settings.DISCORD_BOT_TOKEN, *args, **kwargs)
