import discord

from bot.apps.users.exceptions import UserHasNotRoleError
from bot.dynamic_settings import dynamic_settings
from core.localization import LocaleEnum
from core.logger import logger


def get_member_locale(member: discord.Member, raise_exception: bool = False) -> LocaleEnum | None:
    reverse_roles_map = dynamic_settings.reverse_locale_roles
    for role in member.roles:
        # BUG role can be None if there is no roles: member.roles=[None]
        if role and role.id in reverse_roles_map:
            return LocaleEnum(reverse_roles_map[role.id])

    logger.warning(f'{member}:{member.id} не имеет роли языка')
    if raise_exception:
        raise UserHasNotRoleError()
