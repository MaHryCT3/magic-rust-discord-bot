from bot.bot import MagicRustBot

from .commands import CommandsUnbanTicketsCog


def setup(bot: MagicRustBot):
    bot.add_cog(CommandsUnbanTicketsCog(bot))
