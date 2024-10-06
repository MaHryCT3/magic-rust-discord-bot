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
    locale_roles: dict[LocaleEnum, RoleId] = SettingValue(
        default_factory=dict,
        cast_on_load=cast_dict(LocaleEnum, RoleId),
    )
    # Канал куда будут постятся новости из других соцсетей проекта
    repost_channel: ChannelId = SettingValue(default=0)
    # Тикеты
    ticket_category_id: CategoryId = SettingValue(default=0)
    ticket_history_channel_id: ChannelId = SettingValue(default=0)

    @property
    def reverse_locale_roles(self) -> dict[RoleId, LocaleEnum]:
        return {value: key for key, value in self.locale_roles.items()}

    @property
    def reverse_find_friend_channels(self) -> dict[ChannelId, LocaleEnum]:
        return {value: key for key, value in self.find_friend_channels.items()}


dynamic_settings = DynamicSettings(settings.REDIS_URL, namespace='settings')
