from bot import MagicRustBot

import discord
from discord.ext import commands
from bot.dynamic_settings import dynamic_settings
from bot.apps.users.utils import get_member_locale
from bot.core.localization import LocaleEnum, LocalizationDict

class FindFriendEvents(commands.Cog):
    respond_localization = LocalizationDict({
        LocaleEnum.en: 'Use `/friend` command to find a friend',
        LocaleEnum.ru: 'Для поиска друга воспользуйтесь командой `/friend`',
    })

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        locale = get_member_locale(message.author)
        if not message.channel.id in list(dynamic_settings.find_friend_channels.values()):
            return
        await message.delete()
        await message.author.send(self.respond_localization[locale])