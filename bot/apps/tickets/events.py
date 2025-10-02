from discord.ext.commands import Cog
import discord

from bot import MagicRustBot
from bot.apps.tickets.actions.mark_ticket_as_resolved import MarkTicketAsResolvedAction
from bot.dynamic_settings import dynamic_settings


class TicketEventsCog(Cog):

    def __init__(self, bot: MagicRustBot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        channel = message.channel
        if not message.author.bot:
            return

        if not isinstance(channel, discord.TextChannel):
            return

        if not channel.category_id or channel.category_id != dynamic_settings.ticket_category_id:
            return

        if not message.content.strip() == '/ticket resolve':
            return

        await message.delete()
        await MarkTicketAsResolvedAction(
            channel=message.channel,
            resolved_by=message.author,
        ).execute()
