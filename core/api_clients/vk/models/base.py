from pydantic import BaseModel


class BaseUpdateEvent(BaseModel):
    group_id: int
