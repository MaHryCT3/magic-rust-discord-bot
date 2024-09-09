from pydantic import BaseModel


class LongPollServer(BaseModel):
    key: str
    server: str
    ts: int
