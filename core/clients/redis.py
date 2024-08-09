import json
from typing import Any

from redis import StrictRedis


class RedisNameSpace:
    def __init__(self, url: str, namespace: str) -> None:
        self._redis = StrictRedis.from_url(url)
        self.namespace = namespace

    def get(self, key: str, as_bytes: bool = False) -> Any:
        response = self._redis.get(self.make_key(key))
        if as_bytes:
            return response
        return self._decode_response(response)

    def set(self, key: str, value: Any, expire: int = None):
        if not isinstance(value, bytes):
            value = self._encode_redis_request(value)
        self._redis.set(self.make_key(key), value, ex=expire)

    def mget_by_pattern(self, pattern: str = '*'):
        keys = self._redis.keys(self.make_key(pattern))
        return self._redis.mget(keys)

    def delete(self, key: int) -> int:
        full_key = self.make_key(key)
        return self._redis.delete(full_key)

    def make_key(self, key: str) -> str:
        return f'{self.namespace}:{key}'

    @staticmethod
    def _decode_response(data: bytes | None) -> dict | None:
        if not data:
            return data
        return json.loads(data)

    @staticmethod
    def _encode_redis_request(data: list[dict] | dict | None) -> list[str] | str:
        if isinstance(data, list):
            return [json.dumps(data_unit) for data_unit in data]
        return json.dumps(data, default=str)
