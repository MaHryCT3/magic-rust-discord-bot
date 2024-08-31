from enum import Enum

from pydantic import BaseModel, Field


class ServerTypes(Enum):
    MODDED = 'modded'
    OFFICIAL = 'official'
    VANILLA_X2 = 'vanillax2'


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
