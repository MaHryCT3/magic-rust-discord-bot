import discord
from discord.ext import commands

from bot import MagicRustBot
from bot.apps.find_friends.actions.send_find_friend_create_form import (
    ResendFindFriendCreateForm,
)
from bot.apps.find_friends.ui.create_friend_form import CreateFindFriendFormView
from bot.dynamic_settings import dynamic_settings
from core.localization import LocaleEnum, LocalizationDict


class FindFriendEvents(commands.Cog):
    respond_localization = LocalizationDict(
        {
            LocaleEnum.en: 'Use `/friend` command to find a friend',
            LocaleEnum.ru: 'Для поиска друга воспользуйтесь командой `/friend`',
        }
    )

    def __init__(self, bot: MagicRustBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for view in CreateFindFriendFormView.all_locales_init():
            self.bot.add_view(view)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.flags.ephemeral:
            return
        # эта как бы такая костыльная проверка, типо если сообщение с заявкой, то
        # там будет упоминание автора, а если это сообщение для создания формы,
        # то там его не будет, поэтому его скипаем
        if not message.mentions:
            return

        if message.channel.id not in dynamic_settings.find_friend_channels.values():
            return

        action = ResendFindFriendCreateForm(message.channel)
        await action.execute()
