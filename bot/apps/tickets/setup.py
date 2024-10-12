from bot.bot import MagicRustBot

from .commands import CommandsTicketsCog


def setup(bot: MagicRustBot):
    bot.add_cog(CommandsTicketsCog(bot))
