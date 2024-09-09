from typing import TYPE_CHECKING

import discord
from discord import SlashCommandGroup
from discord.ext import commands

from bot.config import logger
from bot.dynamic_settings import dynamic_settings
from core.localization import LocaleEnum

if TYPE_CHECKING:
    from bot import MagicRustBot


class SettingsCog(commands.Cog):
    settings_group = SlashCommandGroup(
        name='settings',
        description='Настройка бота',
        default_member_permissions=discord.Permissions(
            administrator=True,
            ban_members=True,
        ),
        contexts={discord.InteractionContextType.guild},
    )

    def __init__(self, bot: 'MagicRustBot'):
        self.bot = bot

    @settings_group.command(
        description='Изменить кулдаун на поиск друга, указывать в секундах',
    )
    async def cooldown(
        self,
        ctx: discord.ApplicationContext,
        cooldown: discord.Option(int, description='В секундах'),
    ):
        dynamic_settings.find_friend_cooldown = cooldown
        logger.info(f'{ctx.author}:{ctx.author.id} изменил кулдаун на {cooldown}')
        await ctx.respond(
            f'Кулдаун для поиска друга изменена на {cooldown} секунд',
            ephemeral=True,
        )

    @settings_group.command(
        description='Изменить какая роль отвечает за какой язык',
    )
    async def locale_roles(
        self, ctx: discord.ApplicationContext, locale: discord.Option(LocaleEnum), role: discord.Role
    ):
        current_locale_roles = dynamic_settings.locale_roles
        current_locale_roles[role.id] = locale

        dynamic_settings.locale_roles = current_locale_roles
        logger.info(f'{ctx.author}:{ctx.author.id} изменил маппер языков на роль, значение: {current_locale_roles}')
        await ctx.respond(
            f'Для языка {locale} выбрана роль {role}',
            ephemeral=True,
        )

    @settings_group.command(
        description='Изменить каналы для поиска друга',
    )
    async def friend_channels(
        self,
        ctx: discord.ApplicationContext,
        locale: discord.Option(LocaleEnum),
        channel: discord.TextChannel,
    ):
        current_channels = dynamic_settings.find_friend_channels
        current_channels[locale] = channel.id

        dynamic_settings.find_friend_channels = current_channels
        logger.info(f'{ctx.author}:{ctx.author.id} изменил каналы для поиска друга на {current_channels}')
        await ctx.respond(
            f'Канал для поиска друга для региона {locale} был установлен {channel}',
            ephemeral=True,
        )

    @settings_group.command(
        description='Изменить каналы статуса серверов',
    )
    async def server_status_channels(
        self,
        ctx: discord.ApplicationContext,
        locale: discord.Option(LocaleEnum),
        channel: discord.TextChannel,
    ):
        current_channels = dynamic_settings.server_status_channels
        current_channels[locale] = channel.id
        dynamic_settings.server_status_channels = current_channels
        logger.info(f'{ctx.author}:{ctx.author.id} изменил каналы статуса серверов на {current_channels}')
        await ctx.respond(
            f'Канал статуса серверов для региона {locale} был установлен {channel}',
            ephemeral=True,
        )
