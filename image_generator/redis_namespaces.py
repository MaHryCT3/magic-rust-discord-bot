from image_generator.config import settings
from core.clients.redis import RedisNameSpace

images_storage = RedisNameSpace(url=settings.REDIS_URL, namespace='images')
discord_info_storage = RedisNameSpace(url=settings.REDIS_URL, namespace='discord_info')