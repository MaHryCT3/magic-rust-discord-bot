from .channel_setup import ChannelSetupCog


def setup(bot):
    bot.add_cog(ChannelSetupCog(bot))
