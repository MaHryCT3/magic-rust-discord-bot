from enum import Enum
from typing import Self

from pydantic import BaseModel, Field

LIMIT_LABELS = {
    0: 'NO LIMIT',
    1: 'SOLO',
    2: 'MAX 2',
    3: 'MAX 3',
}


class GameModeTypes(Enum):
    MODDED = 'modded'
    VANILLA = 'vanilla'
    VANILLA_X2 = 'vanillax2'


class ServerTypes(Enum):
    MODDED = 'modded'
    OFFICIAL = 'official'
    VANILLA = 'vanillax2'


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
    gm: GameModeTypes = Field()
    limit: int
    lastupdate: int
    num: int


class MonitoringServerData(BaseModel):
    ip: str
    server_type: ServerTypes = Field(alias='class')
    title: str
    players: int
    joining: int
    queue: int
    maxplayers: int


class CombinedServerData(FullServerData, MonitoringServerData):
    @classmethod
    def combine(cls, monitoring_server_data: MonitoringServerData, full_server_data: FullServerData) -> Self:
        return cls(**(full_server_data.model_dump(by_alias=True) | monitoring_server_data.model_dump(by_alias=True)))
