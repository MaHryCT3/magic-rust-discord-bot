import asyncio
from io import BytesIO
from time import time
from typing import Callable

from PIL import Image
from requests.exceptions import HTTPError

from image_generator.image_generator import (
    get_discord_header_image,
    get_server_status_image,
)
from image_generator.redis_namespaces import images_storage

IMAGE_EXPIRATION_TIME = 600


async def update_server_status_image():
    print('status update started')
    image: Image.Image
    try:
        image = get_server_status_image()
    except HTTPError:
        print('API connection failed')
        return
    with BytesIO() as image_binary:
        image.save(image_binary, 'PNG', compress_level=0)
        image_binary.seek(0)
        images_storage.set('server_status_image', image_binary.getvalue(), IMAGE_EXPIRATION_TIME)
    print('Updated server status image')


async def update_discord_header_image():
    image: Image.Image
    try:
        image = get_discord_header_image()
    except HTTPError:
        print('API connection failed')
        return
    images_storage.set('discord_header_image', image.tobytes(), IMAGE_EXPIRATION_TIME)
    print('Updated discord header image')


async def repeat_every_minute(func: Callable, shift: int = 0, *args, **kwargs):
    seconds_until_minute = lambda: shift + 60 - int(time()) % 60
    # print(func.__name__, 'is sleeping for', seconds_until_minute())
    # await asyncio.sleep(seconds_until_minute())
    while True:
        await asyncio.gather(
            func(*args, **kwargs),
            asyncio.sleep(seconds_until_minute()),
        )


async def main():
    server_status_task = asyncio.create_task(repeat_every_minute(update_server_status_image))
    discord_header_task = asyncio.create_task(repeat_every_minute(update_discord_header_image))
    await asyncio.wait([server_status_task, discord_header_task])


def start_generation():
    get_server_status_image()
    print('Started generation')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()


if __name__ == '__main__':
    start_generation()
