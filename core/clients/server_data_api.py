from dataclasses import dataclass
from json import loads

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
        _ip = str(obj.get('ip'))
        _map = str(obj.get('map'))
        _players = int(obj.get('players'))
        _sleepers = int(obj.get('sleepers'))
        _maxplayers = int(obj.get('maxplayers'))
        _queue = int(obj.get('queue'))
        _joining = int(obj.get('joining'))
        _time = float(obj.get('time'))
        _server = int(obj.get('server'))
        _wipeday = int(obj.get('wipeday'))
        _gm = str(obj.get('gm')) if 'gm' in obj.keys() else None
        _limit = int(obj.get('limit'))
        _lastupdate = int(obj.get('lastupdate'))
        _num = int(obj.get('num'))
        return ServerData(
            _ip,
            _map,
            _players,
            _sleepers,
            _maxplayers,
            _queue,
            _joining,
            _time,
            _server,
            _wipeday,
            _gm,
            _limit,
            _lastupdate,
            _num,
        )


@ttl_cache(ttl=API_GET_REQUEST_CACHE_TIME)
def get_servers_data() -> list[ServerData]:
    data = get(settings.SERVER_API_URL)
    data.raise_for_status()
    data_dict: dict = loads(data.content)
    servers = [
        ServerData.from_dict(server_data)
        for server_data in data_dict.values()
        if server_data['lastupdate'] <= SERVER_LASTUPDATE_TRESHOLD and server_data.get('gm', None) != 'test'
    ]
    return servers
