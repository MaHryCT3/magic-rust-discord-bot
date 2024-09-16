from bot.apps.servicing_posts.services.settings import ServicingPostsSettingsService
from bot.apps.servicing_posts.servicing_cog import ServicingPostsCog
from bot.apps.servicing_posts.settings_cog import ServicingPostsSettingsCog
from bot.bot import MagicRustBot


def setup(bot: MagicRustBot):
    servicing_posts_service = ServicingPostsSettingsService()
    bot.add_cog(ServicingPostsSettingsCog(bot, servicing_posts_service))
    bot.add_cog(ServicingPostsCog(bot, servicing_posts_service))
