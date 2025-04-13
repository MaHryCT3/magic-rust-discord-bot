from dataclasses import dataclass, field

import discord

from bot.apps.tickets.services.review_awaiting import ReviewAwaitingService
from bot.apps.tickets.services.ticket_history_api import TicketHistoryAPI
from bot.apps.tickets.ui.ticket_header.review_embed import ReviewEmbed
from core.actions.abstract import AbstractAction
from core.localization import LocaleEnum


@dataclass
class ConfirmScoreAction(AbstractAction):
    locale: LocaleEnum
    ticket_number: int
    score: int
    ticket_history_message: discord.Message

    _awaiting_review_service: ReviewAwaitingService = field(
        default_factory=ReviewAwaitingService,
        init=False,
    )

    async def action(self):
        await self._save_ticket_score()
        await self._add_review_embed()
        await self._remove_message_review_awaiting()

    async def _save_ticket_score(self):
        await TicketHistoryAPI().update_ticket_review(
            ticket_number=self.ticket_number,
            score=self.score,
        )

    async def _add_review_embed(self):
        review_embed = ReviewEmbed.build(
            locale=self.locale,
            score=self.score,
        )
        await self.ticket_history_message.edit(
            embeds=self.ticket_history_message.embeds + [review_embed],
            view=None,
        )

    async def _remove_message_review_awaiting(self):
        await self._awaiting_review_service.remove_by_message_id(
            self.ticket_history_message.id,
        )
