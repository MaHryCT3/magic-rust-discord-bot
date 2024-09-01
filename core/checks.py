from typing import Collection

import discord


def is_owner(owner_ids: Collection[int]):
    def check(ctx: discord.ApplicationContext) -> bool:
        if ctx.user.id in owner_ids:
            return True
        return False

    return check
