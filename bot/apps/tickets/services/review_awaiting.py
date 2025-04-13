import datetime
from dataclasses import asdict, dataclass

from bot.apps.tickets.constants import REVIEW_AWAITING_NAMESPACE
from bot.config import settings
from core.clients.async_redis import AsyncRedisNameSpace
from core.localization import LocaleEnum


@dataclass
class ReviewAwaitingStruct:
    message_id: int
    user_id: int
    ticket_number: int
    created_at: datetime.datetime
    locale: LocaleEnum


class ReviewAwaitingService:
    def __init__(self):
        self._review_awaiting_storage = AsyncRedisNameSpace(
            url=settings.REDIS_URL,
            namespace=REVIEW_AWAITING_NAMESPACE,
        )

    async def add_review_awaiting(self, review_awaiting: ReviewAwaitingStruct):
        await self._review_awaiting_storage.set(
            review_awaiting.message_id,
            asdict(review_awaiting),
        )

    async def get_by_message_id(self, message_id: int):
        data = await self._review_awaiting_storage.get(message_id)
        if data:
            return self._to_struct(data)

    async def remove_by_message_id(self, message_id: int):
        await self._review_awaiting_storage.delete(message_id)

    async def get_all_awaiting_review(self) -> list[ReviewAwaitingStruct]:
        data = await self._review_awaiting_storage.mget_by_pattern(pattern='*')
        return [self._to_struct(item) for item in data]

    @staticmethod
    def _to_struct(raw_data: dict) -> ReviewAwaitingStruct:
        return ReviewAwaitingStruct(
            message_id=int(raw_data['message_id']),
            user_id=int(raw_data['user_id']),
            ticket_number=int(raw_data['ticket_number']),
            created_at=datetime.datetime.fromisoformat(raw_data['created_at']),
            locale=LocaleEnum(raw_data['locale']),
        )
