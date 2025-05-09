import dataclasses
from dataclasses import asdict

from bot.config import settings
from core.clients.async_redis import AsyncRedisNameSpace


@dataclasses.dataclass
class ActiveVoiceProcessStruct:
    channel_id: int
    message_id: int
    craig_url: str
    voice_record_id: str


class ActiveVoiceProcessStorage:
    def __init__(self) -> None:
        self._storage = AsyncRedisNameSpace(
            url=settings.REDIS_URL,
            namespace='active_voice_record_process',
        )

    async def add_voice_process(self, voice_process: ActiveVoiceProcessStruct):
        await self._storage.set(
            voice_process.voice_record_id,
            asdict(voice_process),
        )

    async def get_all_processes(self) -> list[ActiveVoiceProcessStruct]:
        all_processes = await self._storage.mget_by_pattern('*')
        return [self._to_struct(process) for process in all_processes]

    async def delete_process(self, voice_record_id: str) -> None:
        await self._storage.delete(voice_record_id)

    @staticmethod
    def _to_struct(raw_data: dict) -> ActiveVoiceProcessStruct:
        return ActiveVoiceProcessStruct(
            craig_url=raw_data['craig_url'],
            channel_id=int(raw_data['channel_id']),
            message_id=int(raw_data['message_id']),
            voice_record_id=raw_data['voice_record_id'],
        )
