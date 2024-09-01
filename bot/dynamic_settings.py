from typing import TypeAlias

from bot.config import settings
from core.localization import LocaleEnum
from core.redis_settings import BaseRedisSettings, SettingValue, cast_dict

ChannelId: TypeAlias = int
RoleId: TypeAlias = int


class DynamicSettings(BaseRedisSettings):
    find_friend_cooldown: int = SettingValue(default_factory=int)
    find_friend_channels: dict[LocaleEnum, ChannelId] = SettingValue(
        default_factory=dict,
        cast_on_load=cast_dict(LocaleEnum, ChannelId),
    )
    server_filter_channels: dict[LocaleEnum, ChannelId] = SettingValue(
        default_factory=dict,
        cast_on_load=cast_dict(LocaleEnum, ChannelId),
    )
    locale_roles: dict[RoleId, LocaleEnum] = SettingValue(
        default_factory=dict,
        cast_on_load=cast_dict(RoleId, LocaleEnum),
    )
    server_status_channel: ChannelId = SettingValue(
        cast_on_load=ChannelId,
    )


dynamic_settings = DynamicSettings(settings.REDIS_URL, namespace='settings')
