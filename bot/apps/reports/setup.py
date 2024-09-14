from bot.apps.reports.channel_setup_cog import ChannelSetupCog


def setup(bot):
    bot.add_cog(ChannelSetupCog(bot))
