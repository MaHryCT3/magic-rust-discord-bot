from bot import MagicRustBot
from bot.apps.bot_messages.commands import BotMessagesCommandsCog
from bot.apps.bot_messages.services import DelayedMessageService


def setup(bot: MagicRustBot):
    delayed_message_service = DelayedMessageService()
    bot.add_cog(BotMessagesCommandsCog(bot, delayed_message_service))
