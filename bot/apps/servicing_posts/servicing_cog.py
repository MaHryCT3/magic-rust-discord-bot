import discord
from discord.ext import commands

from bot import MagicRustBot
from bot.apps.servicing_posts.services.settings import ServicingPostsSettingsService
from core.emojis import Emojis
from core.localization import LocaleEnum, LocalizationDict


class ServicingPostsCog(commands.Cog):
    thread_name_localization = LocalizationDict(
        {
            LocaleEnum.en: 'Comments',
            LocaleEnum.ru: 'Комментарии',
        }
    )

    def __init__(self, bot: MagicRustBot, posts_services: ServicingPostsSettingsService):
        self.bot = bot
        self.posts_services = posts_services

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.flags.ephemeral:
            return
        if not message.channel:
            return
        channel_settings = await self.posts_services.get_setting(message.channel.id)
        if not channel_settings:
            return

        if channel_settings.ignore_bot and message.author.bot:
            return
        if channel_settings.remove_bot_msg and message.author.bot:
            return await message.delete()
        if (
            channel_settings.remove_user_msg
            and not message.author.bot
            and not message.author.guild_permissions.administrator
        ):
            return await message.delete()

        if channel_settings.add_like:
            await message.add_reaction(Emojis.LIKE)
        if channel_settings.add_dislike:
            await message.add_reaction(Emojis.DISLIKE)
        if channel_settings.add_threads:
            await message.create_thread(name=self.thread_name_localization[channel_settings.locale])
