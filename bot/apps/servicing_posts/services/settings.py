from dataclasses import asdict

from bot.apps.servicing_posts.constants import SETTINGS_NAMESPACE
from bot.apps.servicing_posts.services.models import ServicingPostSettings
from bot.config import settings
from core.clients.async_redis import AsyncRedisNameSpace
from core.localization import LocaleEnum


class ServicingPostsSettingsService:
    def __init__(self):
        self.servicing_posts_storage = AsyncRedisNameSpace(url=settings.REDIS_URL, namespace=SETTINGS_NAMESPACE)

    async def get_setting(self, channel_id: int) -> ServicingPostSettings | None:
        raw_settings = await self.servicing_posts_storage.get(channel_id)
        if raw_settings:
            return self._serialize_response(raw_settings)

    async def add_setting(self, setting: ServicingPostSettings) -> None:
        await self.servicing_posts_storage.set(setting.channel_id, asdict(setting))

    async def get_all_settings(self, locale: LocaleEnum | None = None) -> list[ServicingPostSettings]:
        raw_settings = await self.servicing_posts_storage.mget_by_pattern()
        parsed_settings = [self._serialize_response(setting) for setting in raw_settings]
        if locale:
            parsed_settings = [setting for setting in parsed_settings if setting.locale == locale]
        return parsed_settings

    async def remove_setting(self, channel_id: int) -> ServicingPostSettings:
        await self.servicing_posts_storage.delete(channel_id)

    async def is_setting_exists(self, channel_id: int) -> bool:
        return bool(await self.get_setting(channel_id))

    @staticmethod
    def _serialize_response(raw_response: dict) -> ServicingPostSettings:
        return ServicingPostSettings(
            channel_id=int(raw_response['channel_id']),
            channel_name=raw_response['channel_name'],
            locale=LocaleEnum(raw_response['locale']),
            add_like=bool(raw_response['add_like']),
            add_dislike=bool(raw_response['add_dislike']),
            add_threads=bool(raw_response['add_threads']),
            ignore_bot=bool(raw_response['ignore_bot']),
            remove_bot_msg=bool(raw_response['remove_bot_msg']),
            remove_user_msg=bool(raw_response.get('remove_user_msg', False)),
        )
