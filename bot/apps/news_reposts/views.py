import discord

from bot.apps.news_reposts.buttons import DeclineNewsButton, PublishNewsButton
from bot.bot import MagicRustBot


class PreviewView(discord.View):
    def __init__(self, bot: MagicRustBot):
        publish_button = PublishNewsButton(bot=bot)
        decline_button = DeclineNewsButton(bot=bot)
        super().__init__(publish_button, decline_button)
