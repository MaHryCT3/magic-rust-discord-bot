from abc import ABC, abstractmethod
from typing import Callable, Collection

import discord


def is_owner(owner_ids: Collection[int]):
    def check(ctx: discord.ApplicationContext) -> bool:
        if ctx.user.id in owner_ids:
            return True
        return False

    return check


class BaseCheck(ABC):
    administrator_allowed: bool = True
    owners_allowed: bool = True

    async def __call__(self, ctx: discord.ApplicationContext) -> bool:
        if self.default_checks(ctx):
            return True
        return await self.check(ctx)

    def default_checks(self, ctx: discord.ApplicationContext) -> bool:
        if self.administrator_allowed:
            if ctx.author.guild_permissions.administrator:
                return True
        elif self.owners_allowed:
            if ctx.user.id in ctx.bot.owner_ids:
                return True
        return False

    @abstractmethod
    async def check(self, ctx: discord.ApplicationContext) -> bool:
        pass


class AdminOnlyCheck(BaseCheck):
    async def check(self, _) -> bool:
        return False


class SpecificRoleCheck(BaseCheck):
    def __init__(self, allowed_roles_ids: list[int]) -> None:
        self.allowed_roles_ids = allowed_roles_ids

    async def check(self, ctx: discord.ApplicationContext) -> bool:
        for role in ctx.user.roles:
            if not role:
                continue
            if role.id in self.allowed_roles_ids:
                return True
        return False


class DynamicSpecificRoleCheck(BaseCheck):
    def __init__(self, allowed_roles_ids_getter: Callable[[], list[int]]) -> None:
        self.allowed_roles_ids_getter = allowed_roles_ids_getter

    async def check(self, ctx: discord.ApplicationContext) -> bool:
        allowed_roles_ids = self.allowed_roles_ids_getter()
        for role in ctx.user.roles:
            if not role:
                continue
            if role.id in allowed_roles_ids:
                return True
        return False
