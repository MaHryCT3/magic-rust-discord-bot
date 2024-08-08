from random import choice

from discord import Color

BLUE_COLORS = (
    Color.blue(),
    Color.blurple(),
    Color.og_blurple(),
    Color.dark_blue(),
)


def get_random_blue_color() -> Color:
    return choice(BLUE_COLORS)
