from PIL import Image

from image_generator.fields import Field, ProgressBar, TextField

MAX_CHARACTERS_SHORT_IMAGE = 2


class ImageTemplate:
    text_fields: list[TextField]
    progress_fields: list[ProgressBar]

    def __init__(
        self,
        main_image: Image.Image,
        text_fields_texture: Image.Image,
        progress_fields_texture: Image.Image | None = None,
    ):
        self.main_image = main_image
        self.text_fields = [TextField.from_field(field) for field in self._get_fields(text_fields_texture)]
        if progress_fields_texture:
            self.progress_fields = [
                ProgressBar.from_field(field) for field in self._get_fields(progress_fields_texture)
            ]

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
        players_count_rendered = self.text_fields[self.text_field_names['players_count']].get_image(
            f'{players}/{max_players}'
        )
        result.paste(progress_rendered, self.progress_fields[0].pivot, progress_rendered)
        result.paste(title_rendered, self.text_fields[0].pivot, title_rendered)
        result.paste(description_rendered, self.text_fields[1].pivot, description_rendered)
        result.paste(players_count_rendered, self.text_fields[2].pivot, players_count_rendered)
        return result


class Header(ImageTemplate):
    text_field_names: dict[str, int] = {'discord_online': 0, 'ingame_online': 1}
    text_field_settings: dict[int, TextField.TextSettings] = {
        text_field_names['discord_online']: TextField.TextSettings(
            font='image_generator/assets/fonts/SF-Pro-Display-Black.otf', font_color=(255, 255, 255, 255)
        ),
        text_field_names['ingame_online']: TextField.TextSettings(
            font='image_generator/assets/fonts/SF-Pro-Display-Black.otf', font_color=(255, 255, 255, 255)
        ),
    }

    server_name_text: str
    server_description_text: str

    def __init__(self, extension_image: Image.Image, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extension_image = extension_image
        self.apply_text_settings_dict(self.text_field_settings)

    def build(self, discord_online: str, ingame_online: str) -> Image.Image:
        result: Image.Image = (
            self.main_image.copy() if len(discord_online) <= MAX_CHARACTERS_SHORT_IMAGE else self.extension_image.copy()
        )
        discord_online_rendered = self.text_fields[self.text_field_names['discord_online']].get_image(discord_online)
        ingame_online_rendered = self.text_fields[self.text_field_names['ingame_online']].get_image(ingame_online)
        result.paste(discord_online_rendered, self.text_fields[0].pivot, discord_online_rendered)
        result.paste(ingame_online_rendered, self.text_fields[1].pivot, ingame_online_rendered)
        return result
