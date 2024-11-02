import datetime
import logging
import time

from bot.config import settings
from core.clients.async_redis import AsyncRedisNameSpace
from core.localization import LocaleEnum

logger = logging.getLogger()


class RedisCooldown:
    cooldown_base_namespace: str = 'cooldown:{}'
    # Хранит unix время начала кулдауна

    def __init__(
        self,
        redis_url: str,
        cooldown_namespace: str,
        default_cooldown_expire_seconds: int = 60 * 60 * 24 * 30,
    ):
        self._storage = AsyncRedisNameSpace(
            url=redis_url,
            namespace=self.cooldown_base_namespace.format(cooldown_namespace),
        )
        # время через которое удалить запись из редиса, если кулдаун больше времени, то будет установлено время кулдауна
        self.default_cooldown_expire_seconds = default_cooldown_expire_seconds

    async def get_user_cooldown_residue(self, user_id: int, cooldown_in_seconds: int) -> float | None:
        cooldown = await self.get_cooldown_start_at(user_id)
        if not self._is_on_cooldown(cooldown, cooldown_in_seconds):
            return None

        cooldown_residue = (cooldown + cooldown_in_seconds) - time.time()
        if cooldown_residue < 0:
            return None
        return cooldown_residue

    async def get_cooldown_end_at(self, user_id: int, cooldown_in_seconds: int) -> float | None:
        cooldown = await self.get_cooldown_start_at(user_id)
        if not self._is_on_cooldown(cooldown, cooldown_in_seconds):
            return None
        return cooldown + cooldown_in_seconds

    async def get_cooldown_start_at(self, user_id: int) -> float | None:
        cooldown = await self._storage.get(user_id)
        return cooldown

    async def is_user_on_cooldown(self, user_id: int, cooldown_in_seconds: int) -> bool:
        cooldown_end_at = await self.get_cooldown_end_at(user_id, cooldown_in_seconds)
        return bool(cooldown_end_at)

    async def set_user_cooldown(self, user_id: int, cooldown_in_seconds: int):
        cooldown_expire = (
            cooldown_in_seconds
            if cooldown_in_seconds > self.default_cooldown_expire_seconds
            else self.default_cooldown_expire_seconds
        )

        await self._storage.set(user_id, time.time(), expire=cooldown_expire)
        logger.info(f'Set cooldown for user_id={user_id} at {time.time()}')

    async def reset_cooldown(self, user_id: int):
        await self._storage.delete(user_id)
        logger.info(f'Cooldown for {user_id} has been reset manual')

    def _is_on_cooldown(self, cooldown_start: float | None, cooldown_in_seconds: int) -> bool:
        if not cooldown_start:
            return False
        now_time = datetime.datetime.now(tz=settings.TIMEZONE).timestamp()
        end_at = cooldown_start + cooldown_in_seconds
        if end_at > now_time:
            return True
        return False


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

    async def is_user_on_cooldown(self, user_id: int, locale: LocaleEnum, cooldown_in_seconds: int) -> bool:
        return await self._cooldown_map[locale].is_user_on_cooldown(
            user_id,
            cooldown_in_seconds=cooldown_in_seconds,
        )

    async def set_user_cooldown(self, user_id: int, locale: LocaleEnum, cooldown_in_seconds: int):
        await self._cooldown_map[locale].set_user_cooldown(
            user_id=user_id,
            cooldown_in_seconds=cooldown_in_seconds,
        )

    async def reset_cooldown(self, user_id: int, locale: LocaleEnum):
        await self._cooldown_map[locale].reset_cooldown(user_id=user_id)
