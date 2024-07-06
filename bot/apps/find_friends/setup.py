from typing import TYPE_CHECKING

from bot.core.redis_cooldown import RedisLocaleCooldown

from .commands import FindFriendsCommands

if TYPE_CHECKING:
    from bot import MagicRustBot


def setup(bot: 'MagicRustBot'):
    redis_cooldown = RedisLocaleCooldown(cooldown_name='find_friend')
    bot.add_cog(FindFriendsCommands(bot, redis_cooldown))
