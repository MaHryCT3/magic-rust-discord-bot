from dataclasses import dataclass

from aiohttp import ClientSession
from cachetools.func import ttl_cache
from requests import get

from core.config import settings

SERVER_LASTUPDATE_TRESHOLD = 45
API_GET_REQUEST_CACHE_TIME = 15


@dataclass
class ServerData:
    ip: str
    map: str
    players: int
    sleepers: int
    maxplayers: int
    queue: int
    joining: int
    time: float
    server: int
    wipeday: int
    gm: str | None
    limit: int
    lastupdate: int
    num: int

    @staticmethod
    def from_dict(obj: dict) -> 'ServerData':
        return ServerData(
            obj.get('ip'),
            obj.get('map'),
            obj.get('players'),
            obj.get('sleepers'),
            obj.get('maxplayers'),
            obj.get('queue'),
            obj.get('joining'),
            obj.get('time'),
            obj.get('server'),
            obj.get('wipeday'),
            obj.get('gm'),
            obj.get('limit'),
            obj.get('lastupdate'),
            obj.get('num'),
        )


@ttl_cache(ttl=API_GET_REQUEST_CACHE_TIME)
def get_servers_data() -> list[ServerData]:
    response = get(settings.SERVER_API_URL)
    response.raise_for_status()
    servers_data: dict = response.json()
    servers = [
        ServerData.from_dict(server_data)
        for server_data in servers_data.values()
        if server_data['lastupdate'] <= SERVER_LASTUPDATE_TRESHOLD and server_data.get('gm', None) != 'test'
    ]
    return servers


@ttl_cache(ttl=API_GET_REQUEST_CACHE_TIME)
async def get_servers_data_async() -> list[ServerData]:
    servers_data: dict
    async with ClientSession() as session:
        async with session.get(settings.SERVER_API_URL) as response:
            servers_data = await response.json(content_type='text/html')
    servers = [
        ServerData.from_dict(server_data)
        for server_data in servers_data.values()
        if server_data['lastupdate'] <= SERVER_LASTUPDATE_TRESHOLD and server_data.get('gm', None) != 'test'
    ]
    return servers
