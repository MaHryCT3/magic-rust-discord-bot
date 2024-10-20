from bot.config import settings
from core.redis_cooldown import RedisCooldown

unban_ticket_cooldown = RedisCooldown(
    redis_url=settings.REDIS_URL,
    cooldown_namespace='unban_ticket',
)
