from bot.config import settings
from core.redis_cooldown import RedisLocaleCooldown

report_cooldown = RedisLocaleCooldown(redis_url=settings.REDIS_URL, cooldown_name='reports')
