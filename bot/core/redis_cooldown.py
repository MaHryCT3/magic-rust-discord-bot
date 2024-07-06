import time

from bot.config import logger, settings
from bot.core.clients.async_redis import AsyncRedisNameSpace
from bot.core.localization import LocaleEnum


class RedisLocaleCooldown:
    cooldown_namespace_template = 'cooldown:{name}:{locale}'
    # Хранит timestamp когда пользователь юзал команду

    def __init__(self, cooldown_name: str):
        self._storage_map: dict[LocaleEnum, AsyncRedisNameSpace] = {
            LocaleEnum(locale): AsyncRedisNameSpace(
                url=settings.REDIS_URL,
                namespace=self.cooldown_namespace_template.format(name=cooldown_name, locale=locale),
            )
            for locale in LocaleEnum
        }

    async def get_user_cooldown_residue(
        self, user_id: int, locale: LocaleEnum, cooldown_in_seconds: int
    ) -> float | None:
        cooldown = await self._storage_map[locale].get(user_id)
        if not cooldown:
            return None

        cooldown_residue = (cooldown + cooldown_in_seconds) - time.time()
        if cooldown_residue < 0:
            return None
        return cooldown_residue

    async def is_user_on_cooldown(self, user_id: int, locale: LocaleEnum) -> bool:
        if await self._storage_map[locale].get(user_id):
            return True
        return False

    async def set_user_cooldown(self, user_id: int, locale: LocaleEnum, cooldown_in_seconds: int):
        await self._storage_map[locale].set(user_id, time.time(), expire=cooldown_in_seconds)
        logger.info(f'Set cooldown for user_id={user_id} at {time.time()}')

    async def reset_cooldown(self, user_id: int, locale: LocaleEnum):
        await self._storage_map[locale].delete(user_id)
        logger.info(f'Cooldown for {user_id} has been reset manual')
