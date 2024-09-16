from bot.config import settings
from core.redis_cooldown import RedisCooldown

select_role_cooldown = RedisCooldown(redis_url=settings.REDIS_URL, cooldown_namespace='select_role')
