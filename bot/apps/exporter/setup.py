from bot import MagicRustBot

from .commands import ExporterCommandCog


def setup(bot: MagicRustBot):
    bot.add_cog(ExporterCommandCog(bot))
