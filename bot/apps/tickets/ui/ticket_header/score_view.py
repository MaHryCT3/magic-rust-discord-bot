from functools import partial

import discord

from bot.apps.tickets.actions.confirm_score import ConfirmScoreAction
from bot.apps.tickets.ui.ticket_header.review_modal import SendReviewModal
from core.emojis import Emojis
from core.localization import LocaleEnum


class TicketScoreView(discord.ui.View):
    style_button_by_score: dict[int, discord.ButtonStyle] = {
        1: discord.ButtonStyle.red,
        2: discord.ButtonStyle.red,
        3: discord.ButtonStyle.grey,
        4: discord.ButtonStyle.green,
        5: discord.ButtonStyle.green,
    }

    def __init__(self, locale: LocaleEnum, ticket_number: int, **kwargs):
        self.locale = locale
        self.ticket_number = ticket_number

        buttons = self._get_stars_buttons()
        kwargs.setdefault('timeout', None)
        super().__init__(*buttons, **kwargs)

    def _get_stars_buttons(self) -> list[discord.ui.Button]:
        buttons = []
        for score in range(1, 6):
            score_button = discord.ui.Button(
                style=self.style_button_by_score[score],
                label=str(score),
                emoji=Emojis.STAR,
                custom_id=f'tickets:{self.ticket_number}:score{score}',
            )
            score_button.callback = partial(self._handle_score, score=score)
            buttons.append(score_button)

        return buttons

    async def _handle_score(self, interaction: discord.Interaction, score: int):
        await ConfirmScoreAction(
            locale=self.locale,
            ticket_number=self.ticket_number,
            score=score,
            ticket_history_message=self.message,
        ).execute()

        modal = SendReviewModal(
            locale=self.locale,
            ticket_history_message=self.message,
            ticket_number=self.ticket_number,
            score=score,
        )
        await interaction.response.send_modal(modal)
