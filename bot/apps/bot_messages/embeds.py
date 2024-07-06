import discord

from bot.core.utils.colors import get_random_blue_color


class SendMessageByBotEmbed(discord.Embed):
    @classmethod
    def build(cls, content: str, image_url: str | None = None):
        embed = cls(color=get_random_blue_color())
        embed.add_field(name='', value=content, inline=False)
        if image_url:
            embed.set_image(url=image_url)
        return embed
