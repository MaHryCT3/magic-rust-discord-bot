from typing import TYPE_CHECKING

from .commands import SettingsCog

if TYPE_CHECKING:
    from bot import MagicRustBot


def setup(bot: 'MagicRustBot'):
    bot.add_cog(SettingsCog(bot))
