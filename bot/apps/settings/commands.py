import io
from typing import TYPE_CHECKING

import discord
from discord import PermissionOverwrite, SlashCommandGroup
from discord.ext import commands

from bot.apps.servicing_posts.services.settings import ServicingPostsSettingsService
from bot.dynamic_settings import dynamic_settings
from core.localization import LocaleEnum
from core.logger import logger

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
    find_friends_subgroup = settings_group.create_subgroup(
        'find_friends',
        description='Настройка команды поиска друга',
    )
    voice_channels_subgroup = settings_group.create_subgroup(
        'voice_channels',
        description='Настройка голосовых комнат',
    )

    tickets_subgroup = settings_group.create_subgroup(
        'tickets',
        description='Настройки тикетов',
    )

    def __init__(self, bot: 'MagicRustBot'):
        self.bot = bot
        self.servicing_posts_settings = ServicingPostsSettingsService()

    @settings_group.command(
        description='Изменить какая роль отвечает за какой язык',
    )
    async def locale_roles(
        self, ctx: discord.ApplicationContext, locale: discord.Option(LocaleEnum), role: discord.Role
    ):
        current_locale_roles = dynamic_settings.locale_roles
        current_locale_roles[locale] = role.id

        dynamic_settings.locale_roles = current_locale_roles
        logger.info(f'{ctx.author}:{ctx.author.id} изменил маппер языков на роль, значение: {current_locale_roles}')
        await ctx.respond(
            f'Для языка {locale} выбрана роль {role.mention}',
            ephemeral=True,
            delete_after=10,
        )

    @find_friends_subgroup.command(
        name='cooldown',
        description='Изменить кулдаун на поиск друга, указывать в секундах',
    )
    async def find_friend_cooldown(
        self,
        ctx: discord.ApplicationContext,
        cooldown: discord.Option(int, description='В секундах'),
    ):
        dynamic_settings.find_friend_cooldown = cooldown
        logger.info(f'{ctx.author}:{ctx.author.id} изменил кулдаун поиска друга на {cooldown}')
        await ctx.respond(
            f'Кулдаун для поиска друга изменен на {cooldown} секунд',
            ephemeral=True,
            delete_after=10,
        )

    @find_friends_subgroup.command(
        name='channels',
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
        await self._make_channel_locale_specific(channel, locale)
        await self._make_channel_non_textable(channel)
        logger.info(f'{ctx.author}:{ctx.author.id} изменил каналы для поиска друга на {current_channels}')
        await ctx.respond(
            f'Канал для поиска друга для региона {locale} был установлен {channel}',
            ephemeral=True,
            delete_after=10,
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
        await self._make_channel_locale_specific(channel, locale)
        await self._make_channel_non_textable(channel)
        logger.info(f'{ctx.author}:{ctx.author.id} изменил каналы статуса серверов на {current_channels}')
        await ctx.respond(
            f'Канал статуса серверов для региона {locale} был установлен {channel}',
            ephemeral=True,
            delete_after=10,
        )

    @settings_group.command(
        description='Изменить канал для репостов',
    )
    async def repost_channel(self, ctx: discord.ApplicationContext, channel: discord.TextChannel):
        dynamic_settings.repost_channel = channel.id
        await self._make_channel_non_textable(channel)
        logger.info(f'{ctx.author}:{ctx.author.id} изменил канал для репостов: {channel.name}:{channel.id}')
        await ctx.respond(
            f'Канал для репостов установлен {channel.mention}',
            ephemeral=True,
            delete_after=10,
        )

    @voice_channels_subgroup.command(
        name='cooldown',
        description='Изменить кулдаун создания голосовых каналов, указывать в секундах',
    )
    async def user_room_create_cooldown(
        self,
        ctx: discord.ApplicationContext,
        cooldown: discord.Option(int, description='В секундах'),
    ):
        dynamic_settings.user_room_create_cooldown = cooldown
        logger.info(f'{ctx.author}:{ctx.author.id} изменил кулдаун создания голосовых каналов на {cooldown}')
        await ctx.respond(
            f'Кулдаун для создания голосовых каналов изменен на {cooldown} секунд',
            ephemeral=True,
            delete_after=10,
        )

    @voice_channels_subgroup.command(
        name='master_channels',
        description='Изменить комнаты создания голосовых каналов',
    )
    async def voice_channels_master_channels(
        self,
        ctx: discord.ApplicationContext,
        locale: discord.Option(LocaleEnum),
        channel: discord.VoiceChannel,
    ):
        current_channels = dynamic_settings.channel_creating_channels
        current_channels[locale] = channel.id
        dynamic_settings.channel_creating_channels = current_channels
        await self._make_channel_locale_specific(channel, locale)
        await self._make_channel_non_textable(channel)
        logger.info(f'{ctx.author}:{ctx.author.id} изменил комнаты создания каналов на {current_channels}')
        await ctx.respond(
            f'Комната создания серверов для региона {locale} была установлена на {channel}',
            ephemeral=True,
            delete_after=10,
        )

    @voice_channels_subgroup.command(
        name='categories',
        description='Изменить разделы для голосовых комнат',
    )
    async def user_rooms_categories(
        self,
        ctx: discord.ApplicationContext,
        locale: discord.Option(LocaleEnum),
        category: discord.CategoryChannel,
    ):
        current_channels = dynamic_settings.user_rooms_categories
        current_channels[locale] = category.id
        dynamic_settings.user_rooms_categories = current_channels
        await self._make_channel_locale_specific(category, locale)
        logger.info(f'{ctx.author}:{ctx.author.id} изменил каналы создания голосовых комнат на {current_channels}')
        await ctx.respond(
            f'Канал создания голосовых комнат для региона {locale} была установлен на {category}',
            ephemeral=True,
            delete_after=10,
        )

    @tickets_subgroup.command(
        name='category',
        description='Изменить категории тикетов',
    )
    async def ticket_category(self, ctx: discord.ApplicationContext, category: discord.CategoryChannel):
        dynamic_settings.ticket_category_id = category.id
        logger.info(f'{ctx.author}:{ctx.author.id} изменил категорию тикетов {category.id}')
        await ctx.respond(
            f'Категория тикетов изменена {category.mention}',
            ephemeral=True,
            delete_after=10,
        )

    @tickets_subgroup.command(
        name='history_channel',
        description='Изменить канал истории тикетов',
    )
    async def tickets_history_channel(self, ctx: discord.ApplicationContext, channel: discord.TextChannel):
        dynamic_settings.ticket_history_channel_id = channel.id
        logger.info(f'{ctx.author}:{ctx.author.id} изменил канал истории тикетов {channel.id}')
        await ctx.respond(
            f'Канал истории тикетов изменен на {channel.mention}',
            ephemeral=True,
            delete_after=10,
        )

    @settings_group.command(description='Выгрузка настроек')
    @commands.is_owner()
    async def dump(self, ctx: discord.ApplicationContext):
        setting_bytes = dynamic_settings.get_settings_bytes()
        await ctx.send(
            file=discord.File(io.BytesIO(setting_bytes), filename='dynamic_settings'),
        )

    @settings_group.command(description='Загрузка настроек')
    @commands.is_owner()
    async def load(self, ctx: discord.ApplicationContext):
        await ctx.respond('Отправь файл с настройкам', delete_after=10)
        next_message: discord.Message = await self.bot.wait_for(
            'message',
            check=lambda message: message.author == ctx.author,
            timeout=30,
        )
        settings_file = next_message.attachments[0]
        settings_bytes = await settings_file.read()
        dynamic_settings.load_settings_from_bytes(settings_bytes)

        await ctx.send('Настройки обновлены', delete_after=10)

    async def _make_channel_non_textable(self, channel: discord.abc.Messageable):
        guild = self.bot.get_main_guild()
        everyone_permissions = PermissionOverwrite()
        everyone_permissions.send_messages = False
        await channel.set_permissions(guild.default_role, overwrite=everyone_permissions)

    async def _make_channel_locale_specific(self, channel: discord.abc.GuildChannel, locale: LocaleEnum):
        guild = self.bot.get_main_guild()
        everyone_permissions = PermissionOverwrite()
        everyone_permissions.view_channel = False
        everyone_permissions.create_public_threads = False
        everyone_permissions.create_private_threads = False
        locale_permissions = PermissionOverwrite()
        locale_permissions.view_channel = True
        locale_permissions.read_message_history = True
        await channel.set_permissions(guild.default_role, overwrite=everyone_permissions)
        await channel.set_permissions(self.bot.get_locale_role(locale), overwrite=locale_permissions)
