from aiocache import Cache, cached
from pydantic import TypeAdapter

from core.api_clients.magic_rust.models import MagicRustBan, MagicRustServerData
from core.clients.http import HTTPClient

SERVER_LASTUPDATE_TRESHOLD = 45
API_GET_REQUEST_CACHE_TIME = 15
API_GET_BANS_REQUEST_CACHE_TIME = 120


class MagicRustAPI:
    def __init__(self, http_client: HTTPClient | None = None):
        self.http_client = http_client or HTTPClient(base_url='https://vk.magicrust.ru/')

    @cached(ttl=API_GET_REQUEST_CACHE_TIME, cache=Cache.MEMORY)
    async def get_server_data(self) -> list[MagicRustServerData]:
        servers_data = await self.http_client.get('api/getDiscordOnline')
        response_json: dict = servers_data.json()
        return TypeAdapter(list[MagicRustServerData]).validate_python(response_json)

    @cached(ttl=API_GET_BANS_REQUEST_CACHE_TIME, cache=Cache.MEMORY)
    async def get_servers_bans(self) -> list[MagicRustBan]:
        bans_data = await self.http_client.get('api/getAllBans')
        response_json: dict = bans_data.json()
        return TypeAdapter(list[MagicRustBan]).validate_python(response_json)

    async def get_server_ban(self, steamid: str) -> MagicRustBan | None:
        bans = await self.get_servers_bans()
        for ban in bans:
            if ban.steamid == steamid:
                return ban
        return None
