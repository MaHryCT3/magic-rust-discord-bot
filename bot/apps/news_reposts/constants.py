from typing import Final

import discord

from bot.apps.news_reposts.services.captures.structs import CapturedNewsSources

DEFAULT_POLL_DURATION_IN_HOURS: Final[int] = 14
COLOR_BY_CAPTURE_SOURCE_MAP: dict[CapturedNewsSources, discord.Color] = {
    CapturedNewsSources.VK: discord.Color.blue(),
}
