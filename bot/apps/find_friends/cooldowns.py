from bot.apps.find_friends.constants import FIND_FRIEND_COOLDOWN_NAMESPACE
from bot.config import settings
from core.redis_cooldown import RedisLocaleCooldown

find_friend_cooldown = RedisLocaleCooldown(redis_url=settings.REDIS_URL, cooldown_name=FIND_FRIEND_COOLDOWN_NAMESPACE)
