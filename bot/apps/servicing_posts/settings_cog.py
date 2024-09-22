import discord
from discord import SlashCommandGroup, TextChannel
from discord.ext import commands

from bot import MagicRustBot
from bot.apps.servicing_posts.services.settings import ServicingPostsSettingsService
from bot.apps.servicing_posts.ui import (
    SelectServicingActionSelect,
    ServicingDeleteChannelsSelect,
    ServicingEditChannelsSelect,
)
from core.localization import LocaleEnum


class ServicingPostsSettingsCog(commands.Cog):
    servicing_posts_group = SlashCommandGroup(
        name='servicing-posts',
        description='Управление обслуживанием постов',
        default_member_permissions=discord.Permissions(
            administrator=True,
            ban_members=True,
        ),
        contexts={discord.InteractionContextType.guild},
    )

    def __init__(self, bot: MagicRustBot, posts_settings: ServicingPostsSettingsService):
        self.bot = bot
        self.posts_settings_service = posts_settings

    @servicing_posts_group.command(description='Добавить канал в обслуживание')
    async def add_channel(self, ctx: discord.ApplicationContext, channel: TextChannel, locale: LocaleEnum):
        select = SelectServicingActionSelect(
            channel_id=channel.id,
            channel_name=channel.name,
            locale=locale,
            servicing_posts_settings=self.posts_settings_service,
        )
        view = discord.ui.View(select)
        await ctx.respond(
            view=view,
            ephemeral=True,
            delete_after=60,
        )

    @servicing_posts_group.command(description='Редактирование обслуживающего канала')
    async def edit_channels(self, ctx: discord.ApplicationContext):
        channels = await self.posts_settings_service.get_all_settings()
        edit_select = ServicingEditChannelsSelect(
            servicing_setting_service=self.posts_settings_service,
            channels_settings=channels,
        )
        view = discord.ui.View(edit_select)
        await ctx.respond(
            view=view,
            ephemeral=True,
        )

    @servicing_posts_group.command(description='Удалить канал из обслуживания')
    async def delete_channel(self, ctx: discord.ApplicationContext):
        channels = await self.posts_settings_service.get_all_settings()
        delete_select = ServicingDeleteChannelsSelect(
            servicing_setting_service=self.posts_settings_service,
            channels_settings=channels,
        )
        view = discord.ui.View(delete_select)
        await ctx.respond(
            view=view,
            ephemeral=True,
            delete_after=60,
        )

    @servicing_posts_group.command(description='Копирование настроек с другого канала')
    async def copy_settings(self, ctx: discord.ApplicationContext, from_channel: TextChannel, to_channel: TextChannel):
        channel_settings = await self.posts_settings_service.get_setting(from_channel.id)
        if not channel_settings:
            await ctx.respond(f'У канала {from_channel.mention}', ephemeral=True)
            return

        channel_settings.channel_id = to_channel.id
        await self.posts_settings_service.add_setting(channel_settings)
        await ctx.respond(
            f'Настройки скопированы с канала {from_channel.mention} в канал {to_channel.mention}',
            ephemeral=True,
        )
