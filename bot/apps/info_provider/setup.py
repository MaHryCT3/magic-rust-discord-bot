from bot import MagicRustBot

from .info_provider import InfoProvider


def setup(bot: MagicRustBot):
    bot.add_cog(InfoProvider(bot))
