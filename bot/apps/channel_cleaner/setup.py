from bot import MagicRustBot

from .channel_cleaner import ChannelCleaner


def setup(bot: MagicRustBot):
    bot.add_cog(ChannelCleaner(bot))
