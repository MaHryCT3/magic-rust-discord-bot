from discord import Client

from bot import MagicRustBot
from bot.apps.bot_messages.embeds import SendMessageByBotEmbed
from bot.apps.bot_messages.services import DelayedMessage


async def send_delayed_message(message: DelayedMessage, bot: Client):
    embed = SendMessageByBotEmbed.build(content=message.embed_content, image_url=message.image_url)
    channel = await bot.fetch_channel(message.channel_id)
    await channel.send(content=message.before_text, embeds=[embed])
