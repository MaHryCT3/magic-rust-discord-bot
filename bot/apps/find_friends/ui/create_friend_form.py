from typing import Self

import discord
from discord import Interaction
from discord.ui import Item

from bot.apps.find_friends.actions.send_find_friend_modal import (
    SendFindFriendModalAction,
)
from bot.apps.find_friends.exceptions import BaseFindFriendsError
from core.emojis import Emojis
from core.localization import LocaleEnum


class CreateFindFriendFormButton(discord.ui.Button):
    async def callback(self, interaction: Interaction):
        action = SendFindFriendModalAction(interaction, interaction.user)
        await action.execute()


class CreateFindFriendFormView(discord.ui.View):

    def __init__(self, locale: LocaleEnum, **kwargs):
        kwargs.setdefault('timeout', None)
        super().__init__(
            CreateFindFriendFormButton(
                emoji=Emojis.PEOPLES,
                custom_id=f'create_form:{locale.value}:button',
            ),
            **kwargs,
        )
        self.locale = locale

    async def on_error(self, error: Exception, item: Item, interaction: Interaction) -> None:
        if isinstance(error, BaseFindFriendsError):
            return await interaction.respond(
                error.message,
                ephemeral=True,
                delete_after=30,
            )
        return await super().on_error(error, item, interaction)

    @classmethod
    def all_locales_init(cls) -> list[Self]:
        return [cls(locale=locale) for locale in LocaleEnum]
