from dataclasses import dataclass

import discord

from bot.apps.tickets.services.ticket_history_api import TicketHistoryAPI
from bot.apps.tickets.ui.ticket_header.review_embed import ReviewEmbed
from core.actions.abstract import AbstractAction
from core.localization import LocaleEnum


@dataclass
class ConfirmReviewAction(AbstractAction):
    locale: LocaleEnum
    ticket_history_message: discord.Message
    ticket_number: int
    score: int
    review: str

    async def action(self):
        await self._save_review()
        await self._update_message_embeds()

    async def _save_review(self):
        await TicketHistoryAPI().update_ticket_review(
            ticket_number=self.ticket_number,
            comment=self.review,
        )

    async def _update_message_embeds(self):
        review_embed = ReviewEmbed.build(
            locale=self.locale,
            score=self.score,
            review=self.review,
        )

        embeds = self.ticket_history_message.embeds.copy()
        if len(embeds) > 1:
            embeds[1] = review_embed
        else:
            embeds += [review_embed]

        await self.ticket_history_message.edit(
            embeds=embeds,
            view=None,
        )
