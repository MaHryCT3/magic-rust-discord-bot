from enum import Enum

from pydantic import BaseModel, Field

LIMIT_LABELS = {
    0: 'NO LIMIT',
    1: 'SOLO',
    2: 'MAX 2',
    3: 'MAX 3',
}


class ServerTypes(Enum):
    MODDED = 'modded'
    OFFICIAL = 'official'
    VANILLA_X2 = 'vanillax2'


class CombinedServerData(BaseModel):
    ip: str
    server_type: ServerTypes
    title: str
    players: int
    sleepers: int
    joining: int
    queue: int
    maxplayers: int
    map: str
    time: float
    server: int
    wipeday: int
    gm: str | None
    limit: int
    lastupdate: int
    num: int

    @staticmethod
    def combine(
        monitoring_server_data: 'MonitoringServerData', full_server_data: 'FullServerData'
    ) -> 'CombinedServerData':
        return CombinedServerData(**(full_server_data.model_dump() | monitoring_server_data.model_dump()))


class FullServerData(BaseModel):
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


class MonitoringServerData(BaseModel):
    ip: str
    server_type: ServerTypes = Field(validation_alias='class')
    title: str
    players: int
    joining: int
    queue: int
    maxplayers: int
