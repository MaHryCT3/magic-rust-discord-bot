from typing import TYPE_CHECKING

import discord
from discord import SlashCommandGroup
from discord.ext import commands

from bot.apps.find_friends.actions.send_find_friend_create_form import (
    ResendFindFriendCreateForm,
)
from bot.apps.find_friends.actions.send_find_friend_modal import (
    SendFindFriendModalAction,
)
from bot.apps.find_friends.cooldowns import find_friend_cooldown
from bot.apps.find_friends.exceptions import (
    BaseFindFriendsError,
)
from bot.apps.users.utils import get_member_locale
from core.localization import LocaleEnum, LocalizationDict
from core.redis_cooldown import RedisLocaleCooldown

if TYPE_CHECKING:
    from bot import MagicRustBot


class FindFriendsCommands(commands.Cog):
    friends_group = SlashCommandGroup(
        name='friends',
        default_member_permissions=discord.Permissions(
            administrator=True,
        ),
        contexts={discord.InteractionContextType.guild},
    )

    def __init__(self, bot: 'MagicRustBot', redis_cooldown: RedisLocaleCooldown) -> None:
        self.bot = bot
        self.redis_cooldown = redis_cooldown

    @friends_group.command(
        description_localizations=LocalizationDict(
            {
                LocaleEnum.en: 'Create a form to find a friend',
                LocaleEnum.ru: 'Создать форму для поиска друга',
            }
        ),
        contexts={discord.InteractionContextType.guild},
    )
    async def create(self, ctx: discord.ApplicationContext) -> None:
        action = SendFindFriendModalAction(ctx.interaction, ctx.author)
        await action.execute()

    @friends_group.command(
        description='Создать сообщение для создания формы поиска друга',
    )
    async def create_form(self, ctx: discord.ApplicationContext):
        action = ResendFindFriendCreateForm(ctx.channel)
        await action.execute()
        await ctx.interaction.response.pong()

    @friends_group.command(description='Убрать кулдаун у пользователя')
    async def reset_cooldown(self, ctx: discord.ApplicationContext, user: discord.Member):
        member_locale = get_member_locale(user, raise_exception=True)
        await find_friend_cooldown.reset_cooldown(user.id, member_locale)
        await ctx.respond(
            f'Кулдаун для поиска друга для {user.mention} обнулен',
            ephemeral=True,
            delete_after=15,
        )

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: BaseFindFriendsError):
        if isinstance(error, BaseFindFriendsError):
            await ctx.respond(error.message, ephemeral=True, delete_after=30)
        raise error
