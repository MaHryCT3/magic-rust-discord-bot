import datetime
from typing import Final

from bot.apps.voice_activity.structs.user_activity import UserActivity
from bot.config import settings
from core.clients.http import HTTPClient


class ActivityAPI:
    ACTIVITY_URI: Final[str] = 'api/v1/activities/'

    def __init__(
        self,
        backend_url: str = settings.ACTIVITY_BACKEND_URL,
        api_token: str = settings.ACTIVITY_BACKEND_API_TOKEN,
    ):
        self.http_client = HTTPClient(
            base_url=backend_url,
            headers={'X-API-Key': api_token},
        )

    async def get_activity(
        self,
        user_id: int | None = None,
        channel_id: int | None = None,
        start_at: datetime.datetime | None = None,
        end_at: datetime.datetime | None = None,
        limit: int = 10,
        offset: int | None = None,
    ) -> list[UserActivity]:
        query = {}
        for query_parameter, query_value in (
            ('user_discord_id', user_id),
            ('channel_id', channel_id),
            ('start_at', start_at),
            ('end_at', end_at),
            ('limit', limit),
            ('offset', offset),
        ):
            if query_value:
                query[query_parameter] = query_value

        response = await self.http_client.get(
            self.ACTIVITY_URI,
            query=query,
        )

        response_data = response.json()

        return [
            UserActivity(
                user_id=int(data['user_discord_id']),
                total_session_duration=datetime.timedelta(seconds=data['total_session_duration']),
                total_microphone_mute_duration=datetime.timedelta(seconds=data['total_microphone_mute_duration']),
                total_sound_disabled_duration=datetime.timedelta(seconds=data['total_sound_disabled_duration']),
            )
            for data in response_data
        ]
