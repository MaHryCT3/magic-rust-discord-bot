import datetime

import discord

from bot.config import settings
from core.utils.colors import get_random_blue_color
from core.utils.format_strings import bold_message


class SendMessageByBotEmbed(discord.Embed):
    @classmethod
    def build(cls, content: str, image_url: str | None = None):
        embed = cls(color=get_random_blue_color())
        embed.add_field(name='', value=content, inline=False)
        if image_url:
            embed.set_image(url=image_url)
        return embed


class QueueMessageEmbed(discord.Embed):
    @classmethod
    def build(
        cls,
        send_time: float,
        channel_name: str,
        channel_mention: str,
        content: str,
        image_url: str | None = None,
    ):
        embed = SendMessageByBotEmbed.build(content, image_url)
        embed.timestamp = datetime.datetime.fromtimestamp(send_time, settings.TIMEZONE)
        embed.insert_field_at(0, name='Канал', value=f'{bold_message(channel_name)} ({channel_mention})')
        return embed
