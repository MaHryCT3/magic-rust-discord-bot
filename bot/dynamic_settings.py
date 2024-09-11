from typing import TypeAlias

from bot.config import settings
from core.localization import LocaleEnum
from core.redis_settings import BaseRedisSettings, SettingValue, cast_dict

ChannelId: TypeAlias = int
CategoryId: TypeAlias = int
RoleId: TypeAlias = int


class DynamicSettings(BaseRedisSettings):
    find_friend_cooldown: int = SettingValue(default=3600)
    find_friend_channels: dict[LocaleEnum, ChannelId] = SettingValue(
        default_factory=dict,
        cast_on_load=cast_dict(LocaleEnum, ChannelId),
    )
    server_status_channels: dict[LocaleEnum, ChannelId] = SettingValue(
        default_factory=dict,
        cast_on_load=cast_dict(LocaleEnum, ChannelId),
    )
    channel_creating_channels: dict[LocaleEnum, ChannelId] = SettingValue(
        default_factory=dict,
        cast_on_load=cast_dict(LocaleEnum, ChannelId),
    )
    user_room_create_cooldown: int = SettingValue(default=15)
    user_rooms_categories: dict[LocaleEnum, CategoryId] = SettingValue(
        default_factory=dict,
        cast_on_load=cast_dict(LocaleEnum, CategoryId),
    )
    locale_roles: dict[RoleId, LocaleEnum] = SettingValue(
        default_factory=dict,
        cast_on_load=cast_dict(RoleId, LocaleEnum),
    )
    # Канал куда будут постятся новости из других соцсетей проекта
    repost_channel: int = SettingValue(default=0)


dynamic_settings = DynamicSettings(settings.REDIS_URL, namespace='settings')
