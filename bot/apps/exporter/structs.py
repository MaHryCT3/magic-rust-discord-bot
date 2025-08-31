from dataclasses import dataclass


@dataclass
class ExportMessage:
    message: str
    time: int
    id: int
    channel: str
    user_id: int
    user_name: str
