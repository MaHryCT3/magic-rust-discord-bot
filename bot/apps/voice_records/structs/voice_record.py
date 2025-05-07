from pydantic import BaseModel
import datetime
from enum import StrEnum


class VoiceProcessStatusEnum(StrEnum):
    AWAITING_PROCESS = 'AWAITING_PROCESS'
    DOWNLOADING_AUDIO = 'DOWNLOADING_AUDIO'
    AUDIO_PROCESS = 'AUDIO_PROCESS'
    AUDIO_TRANSCRIPTION = 'AUDIO_TRANSCRIPTION'
    COMPLETED = 'COMPLETED'


class VoiceRecord(BaseModel):
    id: str
    length: float | None
    recorded_at: datetime.datetime | None
    started_at: datetime.datetime | None
    transcribed_text: str | None
    is_process_error: bool
    process_status: VoiceProcessStatusEnum
