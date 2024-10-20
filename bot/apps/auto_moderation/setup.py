from bot import MagicRustBot

from .reaction_moderation import ReactionModerationCog


def setup(bot: MagicRustBot):
    bot.add_cog(ReactionModerationCog(bot))
