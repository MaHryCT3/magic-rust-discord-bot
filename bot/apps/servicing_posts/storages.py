from bot.apps.servicing_posts.constants import SETTINGS_NAMESPACE
from bot.config import settings
from core.clients.async_redis import AsyncRedisNameSpace

servicing_posts_storage = AsyncRedisNameSpace(url=settings.REDIS_URL, namespace=SETTINGS_NAMESPACE)
