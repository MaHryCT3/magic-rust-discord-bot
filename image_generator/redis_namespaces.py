from core.clients.redis import RedisNameSpace
from global_constants import DISCORD_INFO_NAMESPACE, IMAGES_NAMESPACE
from image_generator.config import settings

images_storage = RedisNameSpace(url=settings.REDIS_URL, namespace=IMAGES_NAMESPACE)
discord_info_storage = RedisNameSpace(url=settings.REDIS_URL, namespace=DISCORD_INFO_NAMESPACE)
