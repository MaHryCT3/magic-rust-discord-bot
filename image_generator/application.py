import asyncio
from io import BytesIO
from time import time
from typing import Callable

from PIL import Image
from requests.exceptions import HTTPError

from global_constants import DISCOR_HEADER_IMAGE_KEY, SERVER_STATUS_IMAGE_KEY
from image_generator.config import logger
from image_generator.image_generator import (
    get_discord_header_image,
    get_server_status_image,
)
from image_generator.redis_namespaces import images_storage

IMAGE_EXPIRATION_TIME = 600


async def update_server_status_image():
    image: Image.Image
    try:
        image = get_server_status_image()
    except HTTPError:
        logger.warn('API connection failed')
        return
    except Exception as e:
        logger.warn(e)
        return
    with BytesIO() as image_binary:
        image.save(image_binary, 'PNG', compress_level=0)
        image_binary.seek(0)
        images_storage.set(SERVER_STATUS_IMAGE_KEY, image_binary.getvalue(), IMAGE_EXPIRATION_TIME)
    logger.info('Updated server status image')


async def update_discord_header_image():
    image: Image.Image
    try:
        image = get_discord_header_image()
    except HTTPError:
        logger.warn('API connection failed')
        return
    except Exception as e:
        logger.warn(e)
        return
    images_storage.set(DISCOR_HEADER_IMAGE_KEY, image.tobytes(), IMAGE_EXPIRATION_TIME)
    logger.info('Updated discord header image')


async def repeat_every_minute(func: Callable, shift: int = 0, *args, **kwargs):
    seconds_until_minute = lambda: shift + 60 - int(time()) % 60
    while True:
        await asyncio.gather(
            func(*args, **kwargs),
            asyncio.sleep(seconds_until_minute()),
        )


def start_status_image_generation():
    logger.info('Started status image generation')
    asyncio.run(repeat_every_minute(update_server_status_image))


def start_discrod_header_generation():
    logger.info('Started discord header generation')
    asyncio.run(repeat_every_minute(update_discord_header_image))
