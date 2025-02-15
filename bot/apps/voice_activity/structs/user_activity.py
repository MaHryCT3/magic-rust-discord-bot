import datetime
from dataclasses import dataclass


@dataclass
class UserActivity:
    user_id: int
    total_session_duration: datetime.timedelta
    total_microphone_mute_duration: datetime.timedelta
    total_sound_disabled_duration: datetime.timedelta

    @property
    def activity_time_duration(self) -> datetime.timedelta:
        return self.total_session_duration - self.total_sound_disabled_duration - self.total_microphone_mute_duration
