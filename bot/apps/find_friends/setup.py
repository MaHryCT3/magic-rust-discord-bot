from typing import TYPE_CHECKING

from bot.config import settings
from core.redis_cooldown import RedisLocaleCooldown
from global_constants import FIND_FRIEND_COOLDOWN_NAMESPACE

from .commands import FindFriendsCommands
from .events import FindFriendEvents

if TYPE_CHECKING:
    from bot import MagicRustBot


def setup(bot: 'MagicRustBot'):
    redis_cooldown = RedisLocaleCooldown(redis_url=settings.REDIS_URL, cooldown_name=FIND_FRIEND_COOLDOWN_NAMESPACE)
    bot.add_cog(FindFriendsCommands(bot, redis_cooldown))
    bot.add_cog(FindFriendEvents(bot))
