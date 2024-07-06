import discord

from bot.config import logger
from bot.core.localization import LocaleEnum
from bot.dynamic_settings import DynamicSettings
from bot.apps.users.exceptions import UserHasNotRoleError


def get_member_locale(member: discord.Member, raise_exception: bool = False) -> LocaleEnum | None:
    roles_map = DynamicSettings().locale_roles
    for role in member.roles:
        if role.id in roles_map:
            return LocaleEnum(roles_map[role.id])

    logger.warning(f'{member}:{member.id} не имеет роли языка')
    if raise_exception:
        raise UserHasNotRoleError()
