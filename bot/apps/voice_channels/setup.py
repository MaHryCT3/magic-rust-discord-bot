from bot import MagicRustBot

from .room_cleaner import RoomCleaner
from .room_creator import RoomCreator


def setup(bot: MagicRustBot):
    bot.add_cog(RoomCreator(bot))
    bot.add_cog(RoomCleaner(bot))
