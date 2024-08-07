from typing import Any, Callable, TypeAlias

from bot.config import logger, settings
from bot.core.clients.redis import RedisNameSpace
from bot.core.localization import LocaleEnum

ChannelId: TypeAlias = int
RoleId: TypeAlias = int


class SettingValue:
    def __init__(
        self,
        default_factory: Callable | None = None,
        cast_on_load: Callable | None = None,
    ):
        self.default_factory = default_factory
        self.cast_on_load = cast_on_load

    def __set_name__(self, owner: type['DynamicSettings'], name: str):
        self.public_name = name
        self._private_name = '_' + name

    def __get__(self, instance: 'DynamicSettings', owner):
        return getattr(instance, self._private_name, None)

    def __set__(self, instance: 'DynamicSettings', value: Any):
        if not instance._load_state:
            instance._storage.set(self.public_name, value)
        else:
            value = value or self.default_factory()
            if self.cast_on_load:
                value = self.cast_on_load(value)
        setattr(instance, self._private_name, value)


def cast_dict(key_cast: Callable, value_cast: Callable) -> Callable[[dict], dict]:
    def cast_func(setting_value: dict):
        return {key_cast(key): value_cast(value) for key, value in setting_value.items()}

    return cast_func


class DynamicSettings:
    find_friend_cooldown: int = SettingValue(default_factory=int)
    find_friend_channels: dict[LocaleEnum, ChannelId] = SettingValue(
        default_factory=dict,
        cast_on_load=cast_dict(LocaleEnum, ChannelId),
    )
    locale_roles: dict[RoleId, LocaleEnum] = SettingValue(
        default_factory=dict,
        cast_on_load=cast_dict(RoleId, LocaleEnum),
    )

    # Происходит загрузка настроек, значит не нужно сохранять их в редис в __set__
    _load_state: bool = False

    def __init__(self):
        self._storage = RedisNameSpace(url=settings.REDIS_URL, namespace='settings')

        self._load_state = True

        logger.info('Load settings from redis')
        for key in self.get_settings_attributes():
            value = self._storage.get(key)
            setattr(self, key, value)
            logger.info(f'{key}={getattr(self, key)}')

        self._load_state = False
        logger.info('Redis settings loaded')

    @classmethod
    def get_settings_attributes(cls):
        return [key for key, value in cls.__dict__.items() if isinstance(value, SettingValue)]


dynamic_settings = DynamicSettings()
