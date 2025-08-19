from aiocache import cached
from pydantic import TypeAdapter

from core.api_clients.magic_rust.models import MagicRustServerData
from core.clients.http import HTTPClient

SERVER_LASTUPDATE_TRESHOLD = 45
API_GET_REQUEST_CACHE_TIME = 15


class MagicRustServerDataAPI:
    def __init__(self, http_client: HTTPClient | None = None):
        self.http_client = http_client or HTTPClient(base_url='https://vk.magicrust.ru/')

    @cached(ttl=API_GET_REQUEST_CACHE_TIME)
    async def get_server_data(self) -> list[MagicRustServerData]:
        servers_data = await self.http_client.get('api/getDiscordOnline')
        response_json: dict = servers_data.json()
        return TypeAdapter(list[MagicRustServerData]).validate_python(response_json)
