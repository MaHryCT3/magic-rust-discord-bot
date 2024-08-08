from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from bot.apps.find_friends.exceptions import (
    BaseFindFriendsError,
    CommandNotConfiguredError,
    UserOnCooldownError,
)
from bot.apps.find_friends.modals import FindFriendModal
from bot.apps.users.utils import get_member_locale
from core.localization import LocaleEnum, LocalizationDict
from core.redis_cooldown import RedisLocaleCooldown
from bot.dynamic_settings import dynamic_settings

if TYPE_CHECKING:
    from bot import MagicRustBot


class FindFriendsCommands(commands.Cog):
    def __init__(self, bot: 'MagicRustBot', redis_cooldown: RedisLocaleCooldown) -> None:
        self.bot = bot
        self.redis_cooldown = redis_cooldown

    @commands.slash_command(
        description_localizations=LocalizationDict(
            {
                LocaleEnum.en: 'Create a form to find a friend',
                LocaleEnum.ru: 'Создать форму для поиска друга',
            }
        ),
        contexts={discord.InteractionContextType.guild},
    )
    async def friend(self, ctx: discord.ApplicationContext) -> None:
        locale = get_member_locale(ctx.author, raise_exception=True)
        cooldown = dynamic_settings.find_friend_cooldown
        channel_id = dynamic_settings.find_friend_channels.get(locale)
        if not cooldown or not channel_id:
            raise CommandNotConfiguredError(locale=locale)
        if cooldown_residue := await self.redis_cooldown.get_user_cooldown_residue(ctx.author.id, locale, cooldown):
            raise UserOnCooldownError(cooldown=cooldown, retry_after=cooldown_residue, locale=locale)

        # NOTE: Важно понимать, что здесь проверяет кулдаун на вызов модалки, но мы должны ограничить отправку сообщения
        # Из модалки, так как пользваотель может открыть одновременно например две модалки
        # Для этого кулдаун устанавливается именно в самой модалке

        await ctx.send_modal(
            FindFriendModal(
                title='',
                locale=locale,
                redis_cooldown=self.redis_cooldown,
            )
        )

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: BaseFindFriendsError):
        await ctx.respond(error.message, ephemeral=True)
