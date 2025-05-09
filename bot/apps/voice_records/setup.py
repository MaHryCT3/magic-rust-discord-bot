from bot import MagicRustBot
from bot.apps.voice_records.voice_process import VoiceProcessCog


def setup(bot: MagicRustBot):
    bot.add_cog(VoiceProcessCog(bot))
