from enum import IntEnum, StrEnum
from typing import Self

from pydantic import BaseModel, Field

from core.utils.date_time import WeekDay

LIMIT_LABELS = {
    0: 'NO LIMIT',
    1: 'SOLO',
    2: 'MAX 2',
    3: 'MAX 3',
}

GAMEMODE_LABELS = {'modded': 'modded', 'vanilla': 'vanilla', 'vanillax2': 'vanilla x2'}


class LimitEnum(IntEnum):
    NO_LIMIT = 0
    SOLO = 1
    MAX_2 = 2
    MAX_3 = 3

    def get_label(self) -> str:
        return LIMIT_LABELS[self.value]


class Maps(StrEnum):
    PRECEDURAL_PLUS = 'Procedural Plus'
    BARREN_PLUS = 'Barren Plus'


class GameModeTypes(StrEnum):
    MODDED = 'modded'
    VANILLA = 'vanilla'
    VANILLA_X2 = 'vanillax2'


class ServerTypes(StrEnum):
    MODDED = 'modded'
    OFFICIAL = 'official'
    VANILLA = 'vanillax2'


class FullServerData(BaseModel):
    ip: str
    map: Maps
    players: int
    sleepers: int
    maxplayers: int
    queue: int
    joining: int
    time: float
    server: int
    wipeday: WeekDay
    gm: GameModeTypes
    limit: LimitEnum
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
