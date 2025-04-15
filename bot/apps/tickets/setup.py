from bot.bot import MagicRustBot

from .commands import CommandsTicketsCog
from .tasks import TasksCog


def setup(bot: MagicRustBot):
    bot.add_cog(CommandsTicketsCog(bot))
    bot.add_cog(TasksCog(bot))
