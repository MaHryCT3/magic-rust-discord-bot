from bot import MagicRustBot

from .news_reposts import NewsRepostsCog


def setup(bot: MagicRustBot):
    bot.add_cog(NewsRepostsCog(bot))
