from bot import MagicRustBot

from .banner_updater import BannerUpdater


def setup(bot: MagicRustBot):
    bot.add_cog(BannerUpdater(bot))
