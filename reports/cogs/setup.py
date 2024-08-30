from .channel_config import ChannelConfigCog


def setup(bot):
    bot.add_cog(ChannelConfigCog(bot))
