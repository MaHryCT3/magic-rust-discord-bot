from enum import IntEnum, StrEnum
from typing import Self

from pydantic import BaseModel, Field, field_validator

from core.utils.date_time import WeekDay


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
    CUSTOM = 'Custom'


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
    map: str
    map_type: Maps = Field(validation_alias='map')
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

    @field_validator('players', 'joining', 'queue', 'maxplayers', 'sleepers')
    @classmethod
    def set_default_0(cls, value, _) -> int:
        if not value:
            return 0
        return value

    @field_validator('map_type', mode='before')
    @classmethod
    def set_default_map_type_custom(cls, value, _) -> str:
        if value not in Maps:
            return Maps.CUSTOM
        return value

    @field_validator('gm', mode='before')
    @classmethod
    def set_default_gm_modded(cls, value, _) -> str:
        if value not in GameModeTypes:
            return GameModeTypes.MODDED
        return value


class MonitoringServerData(BaseModel):
    ip: str
    server_type: ServerTypes = Field(alias='class')
    title: str
    players: int
    joining: int
    queue: int
    maxplayers: int

    @field_validator('players', 'joining', 'queue', 'maxplayers', mode='before')
    @classmethod
    def set_default_0(cls, value, _) -> int:
        if not value:
            return 0
        return value

    @field_validator('server_type', mode='before')
    @classmethod
    def validate_server_type(cls, value, _) -> str:
        try:
            ServerTypes(value)
        except ValueError:
            return ServerTypes.OFFICIAL.value
        else:
            return value


class CombinedServerData(FullServerData, MonitoringServerData):
    @classmethod
    def combine(cls, monitoring_server_data: MonitoringServerData, full_server_data: FullServerData) -> Self:
        return cls(**(full_server_data.model_dump(by_alias=True) | monitoring_server_data.model_dump(by_alias=True)))


LIMIT_LABELS = {
    LimitEnum.NO_LIMIT: 'NO LIMIT',
    LimitEnum.SOLO: 'SOLO',
    LimitEnum.MAX_2: 'MAX 2',
    LimitEnum.MAX_3: 'MAX 3',
}

GAME_MODE_LABELS = {
    GameModeTypes.MODDED: 'modded',
    GameModeTypes.VANILLA: 'vanilla',
    GameModeTypes.VANILLA_X2: 'vanilla x2',
}
