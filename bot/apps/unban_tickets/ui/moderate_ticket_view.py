from typing import Final

import discord

from bot.apps.unban_tickets.actions.moderate_ticket import (
    ApproveUnbanTicket,
    RejectUnbanTicket,
)
from core.utils.regex import get_user_id_from_mention


class ModerateDiscordView(discord.ui.View):
    RCC_LINK: Final[str] = 'https://rustcheatcheck.ru/panel/player/{steam_id}'

    def __init__(self, steam_id: str):
        to_rcc_button = discord.ui.Button(
            label='Открыть RCC',
            url=self.RCC_LINK.format(steam_id=steam_id),
            row=0,
        )

        approve_button = discord.ui.Button(
            style=discord.ButtonStyle.green,
            label='Апрувнуть',
            custom_id='moderate_unban_ticket:approve',
            row=1,
        )
        approve_button.callback = self.approve_button_callback

        reject_button = discord.ui.Button(
            style=discord.ButtonStyle.red,
            label='Отказать',
            custom_id='moderate_unban_ticket:reject',
            row=1,
        )
        reject_button.callback = self.reject_button_callback

        super().__init__(
            to_rcc_button,
            approve_button,
            reject_button,
            timeout=None,
        )

    async def approve_button_callback(self, interaction: discord.Interaction):
        user_id = self._get_user_id(interaction)
        await ApproveUnbanTicket(
            user_id=user_id,
            bot=interaction.client,
            moderate_message=interaction.message,
            initiator_user=interaction.user,
        ).execute()

    async def reject_button_callback(self, interaction: discord.Interaction):
        user_id = self._get_user_id(interaction)
        await RejectUnbanTicket(
            user_id=user_id,
            bot=interaction.client,
            moderate_message=interaction.message,
            initiator_user=interaction.user,
        ).execute()

    def _get_user_id(self, interaction: discord.Interaction):
        return get_user_id_from_mention(interaction.message.content)

    @classmethod
    def for_persist_init(cls):
        return cls(steam_id='')