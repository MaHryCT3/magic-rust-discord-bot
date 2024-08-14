from io import BytesIO
from time import sleep

from requests.exceptions import HTTPError
from schedule import every, run_pending

from global_constants import DISCOR_HEADER_IMAGE_KEY, SERVER_STATUS_IMAGE_KEY
from image_generator.config import logger
from image_generator.image_generator import (
    get_discord_header_image,
    get_server_status_image,
)
from image_generator.redis_namespaces import images_storage

IMAGE_EXPIRATION_TIME = 600


def update_server_status_image():
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


def update_discord_header_image():
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


def start_generation():
    every().minute.at(':00').do(update_server_status_image)
    every().minute.at(':55').do(update_discord_header_image)
    logger.info('Starting generation')
    while True:
        run_pending()
        sleep(1)
