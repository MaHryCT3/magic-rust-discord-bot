from typing import Final

from bot.apps.voice_records.structs.voice_record import VoiceRecord
from bot.config import settings
from core.clients.http import HTTPClient


class VoiceRecordsAPI:
    VOICE_RECORD_URI: Final[str] = '/api/v1/voices-records/{id}'
    START_CRAIG_TRANSCRIBE: Final[str] = '/api/v1/voices-records/craig/start_transcribe'

    def __init__(
        self,
        backend_url: str = settings.VOICE_RECORD_BACKEND_URL,
        api_token: str = settings.VOICE_RECORD_BACKEND_API_TOKEN,
    ):
        self.http_client = HTTPClient(
            base_url=backend_url,
            headers={'X-API-Key': api_token},
        )

    async def get_voice_record(self, voice_record_id: str) -> VoiceRecord:
        response = await self.http_client.get(
            url=self.VOICE_RECORD_URI.format(id=voice_record_id),
        )
        return VoiceRecord(**response.json())

    async def start_craig_transcribe(self, craig_url: str) -> str:
        response = await self.http_client.post(
            url=self.START_CRAIG_TRANSCRIBE,
            body=craig_url,
        )
        return response.json()['id']
