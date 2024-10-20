import dataclasses
from enum import StrEnum

from bot.config import settings
from core.localization import LocaleEnum
from core.redis_cooldown import AsyncRedisNameSpace


class UnbanTicketsStatus(StrEnum):
    AWAITING = 'AWAITING'
    REJECTED = 'REJECTED'
    APPROVED = 'APPROVED'


@dataclasses.dataclass
class UnbanTicketStruct:
    user_id: int
    steam_id: str
    reason: str
    locale: LocaleEnum
    status: UnbanTicketsStatus
    created_at: float


class UnbanTicketsService:
    def __init__(self) -> None:
        self._storage = AsyncRedisNameSpace(
            url=settings.REDIS_URL,
            namespace='unban_tickets',
        )

    async def set_ticket(self, unban_ticket: UnbanTicketStruct):
        await self._storage.set(
            unban_ticket.user_id,
            dataclasses.asdict(unban_ticket),
        )

    async def get_by_user(self, user_id: int) -> UnbanTicketStruct | None:
        raw_data = await self._storage.get(user_id)
        if not raw_data:
            return
        return self._to_struct(raw_data)

    @staticmethod
    def _to_struct(raw_data: dict) -> UnbanTicketStruct:
        return UnbanTicketStruct(
            user_id=int(raw_data['user_id']),
            steam_id=str(raw_data['steam_id']),
            reason=str(raw_data['reason']),
            locale=LocaleEnum(raw_data['locale']),
            status=UnbanTicketsStatus(raw_data['status']),
            created_at=int(raw_data['created_at']),
        )
