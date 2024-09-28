import dataclasses
from functools import cached_property

import discord

from bot.apps.find_friends.cooldowns import find_friend_cooldown
from bot.apps.find_friends.exceptions import (
    CommandNotConfiguredError,
    UserOnCooldownError,
)
from bot.apps.find_friends.modals import FindFriendModal
from bot.apps.users.utils import get_member_locale
from bot.dynamic_settings import dynamic_settings
from core.actions.abstract import AbstractAction
from core.localization import LocaleEnum


@dataclasses.dataclass
class SendFindFriendModalAction(AbstractAction):
    interaction: discord.Interaction
    author: discord.Member

    @cached_property
    def author_locale(self) -> LocaleEnum:
        return get_member_locale(self.author, raise_exception=True)

    async def validate(self):
        cooldown = dynamic_settings.find_friend_cooldown
        channel_id = dynamic_settings.find_friend_channels.get(self.author_locale)
        if not cooldown or not channel_id:
            raise CommandNotConfiguredError(locale=self.author_locale)
        if cooldown_residue := await find_friend_cooldown.get_user_cooldown_residue(
            self.author.id,
            self.author_locale,
            cooldown,
        ):
            raise UserOnCooldownError(cooldown=cooldown, retry_after=cooldown_residue, locale=self.author_locale)

    async def action(self):
        modal = FindFriendModal(locale=self.author_locale)
        await self.interaction.response.send_modal(modal)
