from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

import discord

URL: TypeAlias = str


class CapturedNewsSources(StrEnum):
    VK = 'VK'


@dataclass
class CapturedNews:
    text: str
    images: list[URL]
    files: list[discord.File]
    original_link: str
    poll: discord.Poll
    source: CapturedNewsSources
