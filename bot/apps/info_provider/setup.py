from typing import TYPE_CHECKING

from .info_provider import InfoProvider

if TYPE_CHECKING:
    from bot import MagicRustBot


def setup(bot: 'MagicRustBot'):
    bot.add_cog(InfoProvider(bot))
