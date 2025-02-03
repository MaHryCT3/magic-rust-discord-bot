import json

import aio_pika
from aio_pika import Message
from aio_pika.abc import AbstractChannel

from bot.apps.voice_activity.structs.activity_message import ActivityMessage
from bot.config import settings
from core.logger import logger


class ActivitySenderService:
    def __init__(self):
        self._rabbit_connection = aio_pika.RobustConnection(
            url=settings.RABBIT_MQ_URI,
        )

        self._channel: AbstractChannel | None = None

    async def _on_start_first_call(self):
        await self._rabbit_connection.connect()
        self.channel = await self._rabbit_connection.channel()

    async def send_activity(self, activity_message: ActivityMessage):
        if not self._channel:
            await self._on_start_first_call()

        logger.debug(f'Sending activity: {activity_message}')

        data = {
            'datetime': activity_message.datetime.isoformat(),
            'user_id': activity_message.user_id,
            'channel_id': activity_message.channel_id,
            'channel_type': activity_message.channel_type.name,
            'activity_status': activity_message.activity_status.name,
            'is_microphone_muted': activity_message.is_microphone_muted,
            'is_sound_muted': activity_message.is_sound_muted,
        }

        json_data = json.dumps(data).encode()
        message = Message(
            json_data,
            content_type='application/json',
        )

        await self.channel.default_exchange.publish(
            message,
            routing_key=settings.ACTIVITY_QUEUE_NAME,
        )
