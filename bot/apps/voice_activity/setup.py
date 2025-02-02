from bot import MagicRustBot

from .activity_provider import ActivityProviderCog


def setup(bot: MagicRustBot):
    bot.add_cog(ActivityProviderCog(bot))
