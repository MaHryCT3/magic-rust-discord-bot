import asyncio
from math import ceil

from PIL import Image

from core.api_clients.magic_rust import CombinedServerData, MagicRustServerDataAPI
from global_constants import DISCORD_ONLINE_PRESENCE_KEY, DISCORD_VOICE_PRESENCE_KEY
from image_generator.exceptions import NoAPIDataException
from image_generator.image_templates import Header, ServerCard
from image_generator.redis_namespaces import discord_info_storage

SERVER_LASTUPDATE_TRESHOLD = 45
CARD_IMAGE_PATH = 'image_generator/assets/images/card.png'
CARD_TEXT_IMAGE_PATH = 'image_generator/assets/images/card_text.png'
CARD_PROGRESS_IMAGE_PATH = 'image_generator/assets/images/card_progress.png'
CARD_EMPTY_IMAGE_PATH = 'image_generator/assets/images/card_empty.png'
DISCORD_HEADER_IMAGE_PATH = 'image_generator/assets/images/Main Banner.png'
DISCORD_HEADER_EXTENSION_IMAGE_PATH = 'image_generator/assets/images/Main Banner (extended).png'
DISCORD_HEADER_TEXT_IMAGE_PATH = 'image_generator/assets/images/Main Banner_text.png'
SERVERS_STATUS_CARD_COUNT_HORIZONTAL = 4


def players_to_progress(max_players: int, players: int, joining: int, queue: int) -> list[float]:
    players_sum = players + joining / 2.0 + queue
    if players_sum == 0:
        return []
    map_coef = max_players / players_sum
    map_coef = map_coef if map_coef < 1.0 else 1.0
    return [progress * map_coef for progress in [players / max_players, joining / max_players, queue / max_players]]


def get_discord_data() -> tuple[int, int]:
    voice_presence = discord_info_storage.get(DISCORD_VOICE_PRESENCE_KEY)
    online_presence = discord_info_storage.get(DISCORD_ONLINE_PRESENCE_KEY)
    return (voice_presence, online_presence)


def load_image(path: str) -> Image.Image:
    with Image.open(path) as image_file:
        image = image_file.copy()
    return image


async def get_combined_servers_data() -> list[CombinedServerData]:
    return await MagicRustServerDataAPI().get_combined_servers_data()


def get_server_status_image() -> Image.Image:
    servers_data = asyncio.run(get_combined_servers_data())
    if not servers_data:
        raise NoAPIDataException()
    servers_data.sort(key=lambda item: item.num)
    count = (ceil(len(servers_data) / SERVERS_STATUS_CARD_COUNT_HORIZONTAL), SERVERS_STATUS_CARD_COUNT_HORIZONTAL)
    card_image: Image.Image = load_image(CARD_IMAGE_PATH)
    text_image: Image.Image = load_image(CARD_TEXT_IMAGE_PATH)
    progress_image: Image.Image = load_image(CARD_PROGRESS_IMAGE_PATH)
    card_empty_image: Image.Image = load_image(CARD_EMPTY_IMAGE_PATH)
    card = ServerCard(card_image, text_image, progress_image)
    result = Image.new('RGBA', (card_image.size[0] * count[1], card_image.size[1] * count[0]), (255, 255, 255))
    for i in range(count[0]):
        for j in range(count[1]):
            server_num = i * count[1] + j
            if server_num >= len(servers_data):
                result.paste(card_empty_image, (card_empty_image.size[0] * j, card_empty_image.size[1] * i))
                continue
            server_data = servers_data[server_num]
            progress = players_to_progress(
                server_data.maxplayers, server_data.players, server_data.joining, server_data.queue
            )
            image = card.build(
                server_data.title,
                server_data.map,
                progress,
                server_data.players,
                server_data.maxplayers,
            )
            result.paste(image, (image.size[0] * j, image.size[1] * i))
    return result


def get_discord_header_image() -> Image.Image:
    header_image = load_image(DISCORD_HEADER_IMAGE_PATH)
    header_extension_image = load_image(DISCORD_HEADER_EXTENSION_IMAGE_PATH)
    header_text_image = load_image(DISCORD_HEADER_TEXT_IMAGE_PATH)
    header = Header(header_extension_image, header_image, header_text_image)
    voice_presence, online_presence = get_discord_data()
    return header.build(str(voice_presence), str(online_presence))
