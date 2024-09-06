from typing import TYPE_CHECKING

from .server_status_updater import ServerStatusUpdater

if TYPE_CHECKING:
    from bot import MagicRustBot


def setup(bot: 'MagicRustBot'):
    bot.add_cog(ServerStatusUpdater(bot))
