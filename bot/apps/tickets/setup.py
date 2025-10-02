from bot.bot import MagicRustBot

from .commands import CommandsTicketsCog
from .tasks import TicketTasksCog
from .events import TicketEventsCog


def setup(bot: MagicRustBot):
    bot.add_cog(CommandsTicketsCog(bot))
    bot.add_cog(TicketTasksCog(bot))
    bot.add_cog(TicketEventsCog(bot))
