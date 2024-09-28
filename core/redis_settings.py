import pickle
from typing import Any, Callable, Self

from core.clients.redis import RedisNameSpace


class SettingValue:
    def __init__(
        self,
        default: Any = None,
        default_factory: Callable | None = None,
        cast_on_load: Callable | None = None,
        description: str = '',
    ):
        if default and default_factory:
            raise AttributeError('Either default or default_factory should be provided.')
        self.default = default
        self.default_factory = default_factory
        self.cast_on_load = cast_on_load
        self.description = description

    def __set_name__(self, owner: type['BaseRedisSettings'], name: str):
        self.public_name = name
        self._private_name = '_' + name

    def __get__(self, instance: 'BaseRedisSettings', owner):
        raw_value = instance._storage.get(self.public_name)
        return self._cast_value(raw_value)

    def __set__(self, instance: 'BaseRedisSettings', value: Any):
        instance._storage.set(self.public_name, value)

    def _cast_value(self, value: Any):
        value = value or self.default or (self.default_factory() if self.default_factory else None)
        if value and self.cast_on_load:
            value = self.cast_on_load(value)
        return value


def cast_dict(key_cast: Callable, value_cast: Callable) -> Callable[[dict], dict]:
    def cast_func(setting_value: dict):
        return {key_cast(key): value_cast(value) for key, value in setting_value.items()}

    return cast_func


class BaseRedisSettings:

    def __init__(self, redis_url: str, namespace: str):
        self._storage = RedisNameSpace(url=redis_url, namespace=namespace)

    def get_settings_bytes(self) -> bytes:
        attributes = {key: getattr(self, key) for key in self.get_settings_attributes() if getattr(self, key, None)}
        return pickle.dumps(attributes)

    def load_settings_from_bytes(self, settings_bytes: bytes) -> Self:
        attributes = pickle.loads(settings_bytes)
        for attr, value in attributes.items():
            setattr(self, attr, value)
        return self

    @classmethod
    def get_settings_attributes(cls):
        return [key for key, value in cls.__dict__.items() if isinstance(value, SettingValue)]
