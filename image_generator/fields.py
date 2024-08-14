from dataclasses import dataclass, field
from typing import Self

from PIL import Image, ImageDraw, ImageFont


@dataclass
class Field:
    x_bounds: tuple[int, int]
    y_bounds: tuple[int, int]

    @property
    def center(self) -> tuple[int, int]:
        return ((self.x_bounds[0] + self.x_bounds[1]) / 2, (self.y_bounds[0] + self.y_bounds[1]) / 2)

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
        progress_colors: list[tuple[int, int, int, int]] = field(
            default_factory=lambda: [(0, 200, 0, 255), (0, 0, 200, 255), (200, 0, 0, 255)]
        )

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
            part_bounds = (int(part_start), int(part_start + self.size[0] * part))
            if part_bounds[1] > image.size[0]:
                part_bounds = (part_bounds[0], image.size[0])
            for x in range(*part_bounds):
                for y in range(image.size[1]):
                    image.putpixel((x, y), part_color)
            part_start = part_bounds[1]
        return image
