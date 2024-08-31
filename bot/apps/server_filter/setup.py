from typing import TYPE_CHECKING

from .commands import ServerFilterCommands
from .server_filter import ServerFilter

if TYPE_CHECKING:
    from bot import MagicRustBot


def setup(bot: 'MagicRustBot'):
    bot.add_cog(ServerFilter(bot))
    bot.add_cog(ServerFilterCommands(bot))