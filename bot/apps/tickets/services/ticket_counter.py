from redis.asyncio import ConnectionPool, StrictRedis

from bot.apps.tickets.constants import TICKET_COUNTER_KEY
from bot.config import settings


class TicketCounter:
    def __init__(self):
        connection_pool = ConnectionPool.from_url(settings.REDIS_URL)
        self._redis = StrictRedis(connection_pool=connection_pool, decode_responses=True)

    async def get_next(self) -> int:
        ticket_count = await self._redis.get(TICKET_COUNTER_KEY)
        if ticket_count:
            ticket_count = int(ticket_count) + 1
        return ticket_count or 1

    async def increase(self) -> int:
        next_ticket = await self.get_next()
        await self._redis.set(TICKET_COUNTER_KEY, next_ticket)
        return next_ticket
