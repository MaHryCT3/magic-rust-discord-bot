from dataclasses import dataclass, field
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from requests import get
from json import loads
from config import settings
from time import time
from typing import Any, Callable, Self
import asyncio

CARD_IMAGE_PATH = "image_generator/assets/images/card.png"
CARD_TEXT_IMAGE_PATH = "image_generator/assets/images/card_text.png"
CARD_PROGRESS_IMAGE_PATH = "image_generator/assets/images/card_progress.png"
DISCORD_HEADER_IMAGE_PATH = "image_generator\\assets\\images\\Main Banner.png"
DISCORD_HEADER_EXTENSION_IMAGE_PATH = "image_generator\\assets\\images\\Main Banner (extended).png"
DISCORD_HEADER_TEXT_IMAGE_PATH = "image_generator\\assets\\images\\Main Banner_text.png"


@dataclass
class Field:
    x_bounds: tuple[int, int]
    y_bounds: tuple[int, int]

    @property
    def center(self) -> tuple[int, int]:
        return ((self.x_bounds[0] + self.x_bounds[1])/2, (self.y_bounds[0] + self.y_bounds[1])/2)
    
    @property
    def size(self) -> tuple[int, int]:
        return (self.x_bounds[1] - self.x_bounds[0], self.y_bounds[1] - self.y_bounds[0])
    
    @property
    def pivot(self) -> tuple[int, int]:
        return (self.x_bounds[0], self.y_bounds[0])

class TextField(Field):
    @dataclass
    class TextSettings:
        font: str = 'image_generator/assets/fonts/microsoftsansserif.ttf'
        font_color: tuple[int, int, int, int] = (0, 0, 0, 255)

    PIXELS_PER_PT: float = 1.338307
    text_settings: TextSettings = TextSettings()

    @classmethod
    def from_field(cls, field: Field) -> Self:
        text_field = TextField(field.x_bounds, field.y_bounds)
        return text_field

    def get_image(self, text) -> Image.Image:
        image = Image.new('RGBA', self.size)
        draw = ImageDraw.Draw(image)
        font_size = int(self.size[1] / self.PIXELS_PER_PT)
        font = ImageFont.truetype(self.text_settings.font, font_size)
        draw.text((0, 0), text, self.text_settings.font_color, font=font)
        image.apply_transparency()
        return image

class ProgressBar(Field):
    @dataclass
    class ProgressSettings:
        progress_colors: list[tuple[int, int, int, int]] = field(default_factory=lambda: [(0, 200, 0, 255), (0, 0, 200, 255), (200, 0, 0, 255)])
    
    progress_settings: ProgressSettings = ProgressSettings()

    @classmethod
    def from_field(cls, field: Field) -> Self:
        progress_bar = ProgressBar(field.x_bounds, field.y_bounds)
        return progress_bar
    
    def get_image(self, progress) -> Image.Image:
        image = Image.new('RGBA', self.size)
        part_start = 0
        for i, part in enumerate(progress):
            part_color = self.progress_settings.progress_colors[i]
            part_bounds = (int(part_start), int(part_start + self.size[0]*part))
            if part_bounds[1] > image.size[0]:
                part_bounds = (part_bounds[0], image.size[0])
            for x in range(*part_bounds):
                for y in range(image.size[1]):
                    image.putpixel((x, y), part_color)
            part_start = part_bounds[1]
        return image

class ImageTemplate:
    text_fields: list[TextField]
    progress_fields: list[ProgressBar]

    def __init__(self,
            main_image: Image.Image,
            text_fields_texture: Image.Image,
            progress_fields_texture: Image.Image | None = None):
        self.main_image = main_image
        self.text_fields = [TextField.from_field(field) for field in self._get_fields(text_fields_texture)]
        if progress_fields_texture:
            self.progress_fields = [ProgressBar.from_field(field) for field in self._get_fields(progress_fields_texture)]

    @classmethod
    def _get_fields(cls, field_texture: Image.Image) -> list[Field]:
        fields_dict: dict[int, Field] = {}
        for x in range(field_texture.size[0]):
            for y in range(field_texture.size[1]):
                color = field_texture.getpixel((x, y))
                if color[3] != 0:
                    if not color[0] in fields_dict:
                        fields_dict[color[0]] = Field((x, x), (y, y))
                        continue
                    field = fields_dict[color[0]]
                    if x > field.x_bounds[1]:
                        field.x_bounds = (field.x_bounds[0], x)
                    if x < field.x_bounds[0]:
                        field.x_bounds = (x, field.x_bounds[1])
                    if y > field.y_bounds[1]:
                        field.y_bounds = (field.y_bounds[0], y)
                    if y < field.y_bounds[0]:
                        field.y_bounds = (y, field.y_bounds[0])
        return fields_dict.values()
    
    def apply_text_settings_dict(self, settigns_dict: dict[int, TextField.TextSettings]):
        for field, text_settings in settigns_dict.items():
            self.text_fields[field].text_settings = text_settings
    
    def apply_progress_settings_dict(self, settigns_dict: dict[int, ProgressBar.ProgressSettings]):
        for field, progress_settings in settigns_dict.items():
            self.progress_fields[field].progress_settings = progress_settings


class ServerCard(ImageTemplate):
    text_field_names: dict[str, int] = {'title': 0, 'description': 1, 'players_count': 2}
    text_field_settings: dict[int, TextField.TextSettings] = {
        text_field_names['players_count']: TextField.TextSettings(font_color=(255, 255, 255, 255))
    }
    progress_field_settings: dict[int, ProgressBar.ProgressSettings] = {
        0: ProgressBar.ProgressSettings(progress_colors=[(46, 204, 113, 255), (52, 152, 219, 255), (231, 76, 60)])
    }

    server_name_text: str
    server_description_text: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_text_settings_dict(self.text_field_settings)
        self.apply_progress_settings_dict(self.progress_field_settings)

    def build(self, server_name, server_description, progress, players, max_players) -> Image.Image:
        result: Image.Image = self.main_image.copy()
        progress_rendered = self.progress_fields[0].get_image(progress)
        title_rendered = self.text_fields[self.text_field_names['title']].get_image(server_name)
        description_rendered = self.text_fields[self.text_field_names['description']].get_image(server_description)
        players_count_rendered = self.text_fields[self.text_field_names['players_count']].get_image(f"{players}/{max_players}")
        result.paste(progress_rendered, self.progress_fields[0].pivot, progress_rendered)
        result.paste(title_rendered, self.text_fields[0].pivot, title_rendered)
        result.paste(description_rendered, self.text_fields[1].pivot, description_rendered)
        result.paste(players_count_rendered, self.text_fields[2].pivot, players_count_rendered)
        return result

class Header(ImageTemplate):
    text_field_names: dict[str, int] = {'discord_online': 0, 'ingame_online': 1}
    text_field_settings: dict[int, TextField.TextSettings] = {
        text_field_names['discord_online']: TextField.TextSettings(font="image_generator\\assets\\fonts\\SF-Pro-Display-Black.otf",font_color=(255, 255, 255, 255)),
        text_field_names['ingame_online']: TextField.TextSettings(font="image_generator\\assets\\fonts\\SF-Pro-Display-Black.otf",font_color=(255, 255, 255, 255))
    }

    server_name_text: str
    server_description_text: str

    def __init__(self, extension_image: Image.Image, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extension_image = extension_image
        self.apply_text_settings_dict(self.text_field_settings)

    def build(self, discord_online: str, ingame_online: str) -> Image.Image:
        result: Image.Image = self.main_image.copy() if len(discord_online) < 3 else self.extension_image.copy()
        discord_online_rendered = self.text_fields[self.text_field_names['discord_online']].get_image(discord_online)
        ingame_online_rendered = self.text_fields[self.text_field_names['ingame_online']].get_image(ingame_online)
        result.paste(discord_online_rendered, self.text_fields[0].pivot, discord_online_rendered)
        result.paste(ingame_online_rendered, self.text_fields[1].pivot, ingame_online_rendered)
        return result

def players_to_progress(max_players: int, players: int, joining: int, queue: int) -> list[float]:
    players_sum = players + joining / 2.0 + queue
    if players_sum == 0:
        return []
    map_coef = max_players / players_sum
    map_coef = map_coef if map_coef < 1.0 else 1.0
    return [progress * map_coef for progress in [players/max_players, joining/max_players, queue/max_players]]

def get_servers_data() -> list[dict]:
    data = get(settings.SERVER_API_URL)
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
    print(60-int(time())%60)
    image = get_server_status_image()
    image.save("image_generator\\result\\server_status.png")
    print('updated')

async def repeat_every_minute(func, *args, **kwargs):
    seconds_until_minute = lambda: 60-int(time())%60
    print(seconds_until_minute())
    await asyncio.sleep(seconds_until_minute())
    while True:
        await asyncio.gather(
            func(*args, **kwargs),
            asyncio.sleep(seconds_until_minute()),
        )

async def main():
    server_status_task = asyncio.ensure_future(repeat_every_minute(update_server_status_image))
    await server_status_task

#asyncio.run(main())
get_dictord_header_image().show()