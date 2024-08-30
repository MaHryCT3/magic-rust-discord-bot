from core.redis_cooldown import RedisLocaleCooldown
from reports.bot import settings

report_cooldown = RedisLocaleCooldown(redis_url=settings.REDIS_URL, cooldown_name='reports')
