from core.clients.redis import RedisNameSpace
from image_generator.config import settings

images_storage = RedisNameSpace(url=settings.REDIS_URL, namespace='images')
discord_info_storage = RedisNameSpace(url=settings.REDIS_URL, namespace='discord_info')
