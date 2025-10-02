from bot.bot import MagicRustBot

from .commands import CommandsTicketsCog
from .events import TicketEventsCog
from .tasks import TicketTasksCog


def setup(bot: MagicRustBot):
    bot.add_cog(CommandsTicketsCog(bot))
    bot.add_cog(TicketTasksCog(bot))
    bot.add_cog(TicketEventsCog(bot))
