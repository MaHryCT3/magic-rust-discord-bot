import datetime
from dataclasses import dataclass, field

from bot import MagicRustBot
from bot.apps.tickets.constants import REVIEW_AWAITING_HOURS
from bot.apps.tickets.services.review_awaiting import (
    ReviewAwaitingService,
    ReviewAwaitingStruct,
)
from core.actions.abstract import AbstractAction
from core.logger import logger
from core.shortcuts import get_or_fetch_user_message


@dataclass
class ReviewTimeoutAction(AbstractAction):
    bot: MagicRustBot

    _awaiting_review_service: ReviewAwaitingService = field(
        default_factory=ReviewAwaitingService,
        init=False,
    )

    async def action(self):
        review_awaiting = await self._awaiting_review_service.get_all_awaiting_review()

        for review in review_awaiting:
            if datetime.datetime.now() - review.created_at > datetime.timedelta(hours=REVIEW_AWAITING_HOURS):
                await self._review_timout(review)

    async def _review_timout(self, review: ReviewAwaitingStruct):
        message = await get_or_fetch_user_message(
            bot=self.bot,
            user_id=review.user_id,
            message_id=review.message_id,
        )
        await message.edit(view=None)

        await self._awaiting_review_service.remove_by_message_id(review.message_id)
        logger.info(f'Ожидание оценки тикета #{review.ticket_number} истекло')
