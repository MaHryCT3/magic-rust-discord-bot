from typing import TYPE_CHECKING

from .commands import ImageUpdaterCommands
from .image_updater import ImageUpdater

if TYPE_CHECKING:
    from bot import MagicRustBot


def setup(bot: 'MagicRustBot'):
    bot.add_cog(ImageUpdater(bot))
    bot.add_cog(ImageUpdaterCommands(bot))
