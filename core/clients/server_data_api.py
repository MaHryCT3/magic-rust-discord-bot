import asyncio

from aiocache import cached
from aiohttp import ClientSession
from pydantic import BaseModel

from core.config import settings

SERVER_LASTUPDATE_TRESHOLD = 45
API_GET_REQUEST_CACHE_TIME = 15
LIMIT_LABELS = {
    0: 'NO LIMIT',
    1: 'SOLO',
    2: 'MAX 2',
    3: 'MAX 3',
}

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


def get_servers_data() -> list[ServerData]:
    return asyncio.run(get_servers_data_async())


def is_server_valid(server_data: dict) -> bool:
    return server_data['lastupdate'] <= SERVER_LASTUPDATE_TRESHOLD and server_data.get('gm', None) != 'test'


@cached(ttl=API_GET_REQUEST_CACHE_TIME)
async def get_servers_data_async() -> list[ServerData]:
    servers_data: dict
    async with ClientSession() as session:
        async with session.get(settings.SERVER_API_URL) as response:
            servers_data = await response.json(content_type='text/html')
    servers = [ServerData(**server_data) for server_data in servers_data.values() if is_server_valid(server_data)]
    return servers
