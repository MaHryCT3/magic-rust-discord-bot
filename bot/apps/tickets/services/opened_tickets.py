import dataclasses
import datetime

from bot.apps.tickets.constants import (
    OPENED_TICKETS_NAMESPACE,
    USER_TICKET_CHANNEL_NAMESPACE,
)
from bot.config import settings
from core.clients.async_redis import AsyncRedisNameSpace
from core.localization import LocaleEnum


@dataclasses.dataclass
class OpenedTicketStruct:
    locale: LocaleEnum
    user_id: int
    channel_id: int
    created_at: datetime.datetime
    ticket_number: int
    user_steam: str
    description: str
    resolved_at: datetime.datetime | None = None


class OpenedTicketsService:
    def __init__(self):
        # хранит по айди канала информацию по тикету
        self._storage_ticket = AsyncRedisNameSpace(url=settings.REDIS_URL, namespace=OPENED_TICKETS_NAMESPACE)
        # маппер чтобы найти айди канала у юзера
        self._user_to_channel = AsyncRedisNameSpace(url=settings.REDIS_URL, namespace=USER_TICKET_CHANNEL_NAMESPACE)

    async def is_user_ticket_exists(self, user_id: int) -> bool:
        return bool(await self._user_to_channel.get(user_id))

    async def get_user_ticket_by_user_id(self, user_id: int) -> OpenedTicketStruct | None:
        channel_id = await self._user_to_channel.get(user_id)
        return await self.get_user_ticket_by_channel_id(channel_id)

    async def get_user_ticket_by_channel_id(self, channel_id: int) -> OpenedTicketStruct | None:
        data = await self._storage_ticket.get(channel_id)
        if data:
            return self._to_struct(data)

    async def set_user_ticket(self, ticket: OpenedTicketStruct):
        await self._storage_ticket.set(ticket.channel_id, dataclasses.asdict(ticket))
        await self._user_to_channel.set(ticket.user_id, ticket.channel_id)

    async def delete_user_ticket(self, ticket: OpenedTicketStruct):
        await self._storage_ticket.delete(ticket.channel_id)
        await self._user_to_channel.delete(ticket.user_id)

    async def get_all_tickets(self) -> list[OpenedTicketStruct]:
        data = await self._storage_ticket.mget_by_pattern(pattern='*')
        return [self._to_struct(item) for item in data]

    @staticmethod
    def _to_struct(raw_data: dict) -> OpenedTicketStruct:
        resolved_at = raw_data.get('resolved_at')
        return OpenedTicketStruct(
            user_id=int(raw_data['user_id']),
            channel_id=int(raw_data['channel_id']),
            ticket_number=int(raw_data['ticket_number']),
            locale=LocaleEnum(raw_data['locale']),
            created_at=datetime.datetime.fromisoformat(raw_data['created_at']),
            user_steam=raw_data['user_steam'],
            description=raw_data['description'],
            resolved_at=datetime.datetime.fromisoformat(resolved_at) if resolved_at else None,
        )
