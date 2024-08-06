import discord

from bot.apps.users.exceptions import UserHasNotRoleError
from bot.config import logger
from bot.core.localization import LocaleEnum
from bot.dynamic_settings import dynamic_settings


def get_member_locale(member: discord.Member, raise_exception: bool = False) -> LocaleEnum | None:
    roles_map = dynamic_settings.locale_roles
    for role in member.roles:
        # BUG role can be None if there is no roles: member.roles=[None]
        if role and role.id in roles_map:
            return LocaleEnum(roles_map[role.id])

    logger.warning(f'{member}:{member.id} не имеет роли языка')
    if raise_exception:
        raise UserHasNotRoleError()
