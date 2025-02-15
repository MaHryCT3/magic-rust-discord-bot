from bot import MagicRustBot

from .activity_provider import ActivityProviderCog
from .activity_stats import ActivityStatusCog


def setup(bot: MagicRustBot):
    bot.add_cog(ActivityProviderCog(bot))
    bot.add_cog(ActivityStatusCog(bot))
