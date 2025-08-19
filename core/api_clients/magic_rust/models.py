from enum import IntEnum, StrEnum

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
    PROCEDURAL = 'Procedural'
    BARREN = 'Barren'
    CUSTOM = 'Custom'


class GameModeTypes(StrEnum):
    MODDED = 'modded'
    VANILLA = 'vanilla'
    VANILLA_X2 = 'vanillax2'
    CASUAL = 'casual'


class MagicRustServerData(BaseModel):
    ip: str
    connect: str
    server_number: int
    title: str
    short_title: str
    map_type: Maps = Field(validation_alias='map')
    map: str
    game_mode: GameModeTypes
    player_limit: LimitEnum
    players_online: int = Field(validation_alias='players')
    players_joining: int = Field(validation_alias='joining')
    players_in_queue: int = Field(validation_alias='queue')
    players_max: int = Field(validation_alias='maxplayers')
    wipe_day: WeekDay = Field(validation_alias='wipeday')

    @field_validator('map_type', mode='before')
    @classmethod
    def set_default_map_type(cls, value, _) -> str:
        if Maps.PROCEDURAL.lower() in value.lower():
            return Maps.PROCEDURAL
        elif Maps.BARREN.lower() in value.lower():
            return Maps.BARREN
        elif value not in Maps:
            return Maps.CUSTOM
        return value


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
    GameModeTypes.CASUAL: 'casual',
}
