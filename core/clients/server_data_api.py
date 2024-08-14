import asyncio

from aiohttp import ClientSession
from cachetools.func import ttl_cache
from pydantic import BaseModel

from core.config import settings

SERVER_LASTUPDATE_TRESHOLD = 45
API_GET_REQUEST_CACHE_TIME = 15


class ServerData(BaseModel):
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
    def from_dict(data_dict: dict) -> 'ServerData':
        return ServerData(**data_dict)


def get_servers_data() -> list[ServerData]:
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(get_servers_data_async())
    loop.close()
    return result


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
