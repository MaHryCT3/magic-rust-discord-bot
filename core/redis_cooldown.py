import logging
import time

from core.clients.async_redis import AsyncRedisNameSpace
from core.localization import LocaleEnum

logger = logging.getLogger()


class RedisCooldown:
    cooldown_base_namespace: str = 'cooldown:{}'
    # Хранит unix время начала кулдауна

    def __init__(self, redis_url: str, cooldown_namespace: str):
        self._storage = AsyncRedisNameSpace(
            url=redis_url,
            namespace=self.cooldown_base_namespace.format(cooldown_namespace),
        )

    async def get_user_cooldown_residue(self, user_id: int, cooldown_in_seconds: int) -> float | None:
        cooldown = await self.get_cooldown_start_at(user_id)
        if not cooldown:
            return None

        cooldown_residue = (cooldown + cooldown_in_seconds) - time.time()
        if cooldown_residue < 0:
            return None
        return cooldown_residue

    async def get_cooldown_end_at(self, user_id: int, cooldown_in_seconds: int) -> float | None:
        cooldown = await self.get_cooldown_start_at(user_id)
        if not cooldown:
            return None
        return cooldown + cooldown_in_seconds

    async def get_cooldown_start_at(self, user_id: int) -> float | None:
        cooldown = await self._storage.get(user_id)
        return cooldown

    async def is_user_on_cooldown(self, user_id: int) -> bool:
        if await self._storage.get(user_id):
            return True
        return False

    async def set_user_cooldown(self, user_id: int, cooldown_in_seconds: int):
        await self._storage.set(user_id, time.time(), expire=cooldown_in_seconds)
        logger.info(f'Set cooldown for user_id={user_id} at {time.time()}')

    async def reset_cooldown(self, user_id: int):
        await self._storage.delete(user_id)
        logger.info(f'Cooldown for {user_id} has been reset manual')


class RedisLocaleCooldown:
    """
    Выступает как прокси на 'RedisCooldown', используя его же методы, но выбирает куладаун
    в зависимости от переданного locale
    """

    cooldown_namespace_template = '{name}:{locale}'

    def __init__(self, redis_url: str, cooldown_name: str):
        self._cooldown_map: dict[LocaleEnum, RedisCooldown] = {
            LocaleEnum(locale): RedisCooldown(
                redis_url=redis_url,
                cooldown_namespace=self.cooldown_namespace_template.format(name=cooldown_name, locale=locale),
            )
            for locale in LocaleEnum
        }

    async def get_user_cooldown_residue(
        self, user_id: int, locale: LocaleEnum, cooldown_in_seconds: int
    ) -> float | None:
        return await self._cooldown_map[locale].get_user_cooldown_residue(
            user_id=user_id,
            cooldown_in_seconds=cooldown_in_seconds,
        )

    async def get_cooldown_end_at(self, user_id: int, locale: LocaleEnum, cooldown_in_seconds: int) -> float | None:
        return await self._cooldown_map[locale].get_cooldown_end_at(
            user_id=user_id,
            cooldown_in_seconds=cooldown_in_seconds,
        )

    async def get_cooldown_start_at(self, user_id: int, locale: LocaleEnum) -> float | None:
        return await self._cooldown_map[locale].get_cooldown_start_at(user_id=user_id)

    async def is_user_on_cooldown(self, user_id: int, locale: LocaleEnum) -> bool:
        return await self._cooldown_map[locale].is_user_on_cooldown(user_id)

    async def set_user_cooldown(self, user_id: int, locale: LocaleEnum, cooldown_in_seconds: int):
        await self._cooldown_map[locale].set_user_cooldown(
            user_id=user_id,
            cooldown_in_seconds=cooldown_in_seconds,
        )

    async def reset_cooldown(self, user_id: int, locale: LocaleEnum):
        await self._cooldown_map[locale].reset_cooldown(user_id=user_id)
