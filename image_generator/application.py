from image_generator.image_generator import get_server_status_image, get_discord_header_image
from image_generator.redis_namespaces import images_storage
from PIL import Image
from time import time
from requests.exceptions import HTTPError
import asyncio

IMAGE_EXPIRATION_TIME = 600

async def update_server_status_image():
    image: Image.Image
    try:
        image = get_server_status_image()
    except HTTPError:
        print("API connection failed")
        return
    images_storage.set('server_status_image', image.tobytes(), IMAGE_EXPIRATION_TIME)
    print("Updated server status image")

async def update_discord_header_image():
    image: Image.Image
    try:
        image = get_discord_header_image()
    except HTTPError:
        print("API connection failed")
        return
    images_storage.set('discord_header_image', image.tobytes(), IMAGE_EXPIRATION_TIME)
    print("Updated discord header image")

async def repeat_every_minute(func, shift:int = 0, *args, **kwargs):
    seconds_until_minute = lambda: shift + 60 - int(time()) % 60
    await asyncio.sleep(seconds_until_minute())
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
    print('Started generation')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

if __name__ == "__main__":
    start_generation()