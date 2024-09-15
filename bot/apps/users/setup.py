from bot.apps.users.spawn_message_cog import SpawMessageCog
from bot.bot import MagicRustBot


def setup(bot: MagicRustBot):
    bot.add_cog(SpawMessageCog(bot))
