from bot import MagicRustBot

from .server_status_updater import ServerStatusUpdater


def setup(bot: MagicRustBot):
    bot.add_cog(ServerStatusUpdater(bot))
