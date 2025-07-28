import asyncio

from discord import Cog
from discord.ext import tasks

from bot import MagicRustBot
from bot.apps.tickets.actions.close_resolved_tickets import CloseResolvedTicketsAction
from bot.apps.tickets.actions.review_timeout import ReviewTimeoutAction
from core.utils.decorators import suppress_exceptions


class TasksCog(Cog):
    def __init__(self, bot: MagicRustBot):
        self.bot = bot
        self.guild = None

    @Cog.listener()
    async def on_ready(self):
        self.guild = await self.bot.get_or_fetch_main_guild()

        await self.bot.wait_until_ready()
        self.close_resolved_tickets.start()
        self.timeout_all_reviews.start()

    def cog_unload(self) -> None:
        self.close_resolved_tickets.stop()
        self.timeout_all_reviews.stop()

    @tasks.loop(minutes=5)
    @suppress_exceptions
    async def close_resolved_tickets(self):
        await asyncio.sleep(10)
        await CloseResolvedTicketsAction(self.guild).execute()

    @tasks.loop(minutes=30)
    @suppress_exceptions
    async def timeout_all_reviews(self):
        await ReviewTimeoutAction(self.bot).execute()
