from image_generator.image_templates import ServerCard, Header
from image_generator.config import settings
from PIL import Image
from requests import get
from requests.exceptions import HTTPError
from json import loads
from time import time
import asyncio

CARD_IMAGE_PATH = "image_generator/assets/images/card.png"
CARD_TEXT_IMAGE_PATH = "image_generator/assets/images/card_text.png"
CARD_PROGRESS_IMAGE_PATH = "image_generator/assets/images/card_progress.png"
DISCORD_HEADER_IMAGE_PATH = "image_generator\\assets\\images\\Main Banner.png"
DISCORD_HEADER_EXTENSION_IMAGE_PATH = "image_generator\\assets\\images\\Main Banner (extended).png"
DISCORD_HEADER_TEXT_IMAGE_PATH = "image_generator\\assets\\images\\Main Banner_text.png"

def players_to_progress(max_players: int, players: int, joining: int, queue: int) -> list[float]:
    players_sum = players + joining / 2.0 + queue
    if players_sum == 0:
        return []
    map_coef = max_players / players_sum
    map_coef = map_coef if map_coef < 1.0 else 1.0
    return [progress * map_coef for progress in [players/max_players, joining/max_players, queue/max_players]]

def get_servers_data() -> list[dict]:
    data = get(settings.SERVER_API_URL)
    data.raise_for_status()
    data_dict: dict = loads(data.content)
    server_count = 0
    actual_servers = []
    for server_data in data_dict.values():
        if server_data['lastupdate'] > 45:
            continue
        server_count += 1
        actual_servers.append(server_data)
    return actual_servers

def load_image(path: str) -> Image.Image:
    image: Image.Image
    with Image.open(path) as image_file:
        image = image_file.copy()
    return image

def get_server_status_image() -> Image.Image:
    count = (6, 4)
    servers_data = get_servers_data()
    card_image: Image.Image = load_image(CARD_IMAGE_PATH)
    text_image: Image.Image = load_image(CARD_TEXT_IMAGE_PATH)
    progress_image: Image.Image = load_image(CARD_PROGRESS_IMAGE_PATH)
    card = ServerCard(card_image, text_image, progress_image)
    result = Image.new('RGBA', (progress_image.size[0]*count[1], progress_image.size[1]*count[0]))
    for i in range(count[0]):
        for j in range(count[1]):
            server_data = servers_data[i*count[1] + j]
            progress = players_to_progress(server_data['maxplayers'], server_data['players'], server_data['joining'], server_data['queue'])
            image = card.build(f'MAGIC RUST #{server_data["num"]}', server_data["map"], progress, server_data['players'], server_data['maxplayers'])
            result.paste(image, (image.size[0]*j, image.size[1]*i))
    return result

def get_dictord_header_image() -> Image.Image:
    header_image = load_image(DISCORD_HEADER_IMAGE_PATH)
    header_extension_image = load_image(DISCORD_HEADER_EXTENSION_IMAGE_PATH)
    header_text_image = load_image(DISCORD_HEADER_TEXT_IMAGE_PATH)
    header = Header(header_extension_image, header_image, header_text_image)
    return header.build('820', '46,191')

async def update_server_status_image():
    image: Image.Image
    try:
        image = get_server_status_image()
    except HTTPError:
        print("API connection failed")
        return
    #image.save("image_generator\\result\\server_status.png")
    print("Updated server status image")

async def repeat_every_minute(func, *args, **kwargs):
    seconds_until_minute = lambda: 60-int(time())%60
    await asyncio.sleep(seconds_until_minute())
    while True:
        await asyncio.gather(
            func(*args, **kwargs),
            asyncio.sleep(seconds_until_minute()),
        )

async def main():
    server_status_task = asyncio.ensure_future(repeat_every_minute(update_server_status_image))
    #discord_header_task = asyncio.ensure_future(repeat_every_minute(update_server_status_image))
    await server_status_task
    #await discord_header_task

def start_generation():
    print('Started generation')
    asyncio.run(main())

if __name__ == "__main__":
    start_generation()