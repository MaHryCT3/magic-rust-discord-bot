import datetime
from dataclasses import asdict, dataclass, field
from typing import Self
from uuid import UUID, uuid4

from bot.config import settings
from core.clients.async_redis import AsyncRedisNameSpace
from core.logger import logger


@dataclass
class DelayedMessage:
    channel_id: int
    channel_name: str
    channel_mention: str
    send_time: float
    before_text: str | None = None
    embed_content: str | None = None
    image_url: str | None = None
    uuid: UUID = field(default_factory=uuid4)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            channel_id=int(data['channel_id']),
            channel_name=data['channel_name'],
            channel_mention=data['channel_mention'],
            send_time=float(data['send_time']),
            before_text=data['before_text'],
            embed_content=data['embed_content'],
            image_url=data['image_url'],
            uuid=UUID(data['uuid']),
        )


class DelayedMessageService:
    def __init__(self):
        self._storage = AsyncRedisNameSpace(
            url=settings.REDIS_URL,
            namespace='delayed_messages',
        )

    async def get_messages(self) -> list[DelayedMessage]:
        delayed_messages = await self._storage.mget_by_pattern()
        return [DelayedMessage.from_dict(message) for message in delayed_messages]

    async def add_message(self, message: DelayedMessage):
        logger.info(f'add delayed message {message}')
        await self._storage.set(message.uuid, message.to_dict())

    async def remove_message(self, uuid: UUID):
        logger.info(f'remove delayed message with uuid: {uuid}')
        await self._storage.delete(uuid)

    async def get_messages_to_send(self) -> list[DelayedMessage]:
        now_time = datetime.datetime.now(tz=settings.TIMEZONE).timestamp()

        delayed_messages = await self.get_messages()
        messages_to_send = [message for message in delayed_messages if now_time >= message.send_time]
        if not messages_to_send:
            return []

        # clear queue
        for message_to_send in messages_to_send:
            await self.remove_message(message_to_send.uuid)

        return messages_to_send

    async def clear_messages(self):
        await self._storage.delete_by_pattern('*')
