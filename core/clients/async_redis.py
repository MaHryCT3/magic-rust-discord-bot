import json
from typing import Any

from redis.asyncio import ConnectionPool, StrictRedis


class AsyncRedisNameSpace:
    def __init__(self, url: str, namespace: str) -> None:
        connection_pool = ConnectionPool.from_url(url)
        self._redis = StrictRedis(connection_pool=connection_pool, decode_responses=True)
        self.namespace = namespace

    async def get(self, key: str, as_bytes: bool = False) -> Any:
        response = await self._redis.get(self.make_key(key))
        if as_bytes:
            return response
        return self._decode_response(response)

    async def set(self, key: str, value: Any, expire: int = None):
        value = self._encode_redis_request(value)
        await self._redis.set(self.make_key(key), value, ex=expire)

    async def mget_by_pattern(self, pattern: str = '*'):
        keys = await self._redis.keys(self.make_key(pattern))
        return [self._decode_response(answer) for answer in await self._redis.mget(keys)]

    async def delete(self, key: str) -> int:
        full_key = self.make_key(key)
        return await self._redis.delete(full_key)

    async def delete_by_pattern(self, pattern: str = '*'):
        keys = await self._redis.keys(self.make_key(pattern))
        return await self._redis.delete(*keys)

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
