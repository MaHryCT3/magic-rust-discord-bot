import dataclasses
from functools import cached_property

import discord
import sentry_sdk
from redis import ConnectionPool, StrictRedis

from bot.apps.find_friends.ui.create_friend_form import CreateFindFriendFormView
from bot.config import settings
from bot.dynamic_settings import dynamic_settings
from core.actions.abstract import AbstractAction
from core.localization import LocaleEnum
from core.logger import logger


@dataclasses.dataclass
class ResendFindFriendCreateForm(AbstractAction):
    channel: discord.TextChannel

    _last_form_message_redis_key_template = 'find_friend_form:{locale}'
    _localization_image = {
        LocaleEnum.ru: 'https://i.imgur.com/9pQ2Nix.jpeg',
        LocaleEnum.en: 'https://i.imgur.com/bCSJetE.jpeg',
    }

    @cached_property
    def locale(self):
        return dynamic_settings.reverse_find_friend_channels[self.channel.id]

    @property
    def last_message_redis_key(self) -> str:
        return self._last_form_message_redis_key_template.format(locale=self.locale)

    def __post_init__(self):
        self._redis = StrictRedis.from_pool(
            ConnectionPool.from_url(url=settings.REDIS_URL, decode_responses=True),
        )

    async def action(self):
        embed = self._get_embed()
        view = CreateFindFriendFormView(self.locale)
        message = await self.channel.send(embed=embed, view=view)

        await self._delete_previous_message()
        self._redis.set(self.last_message_redis_key, message.id)

    def _get_embed(self) -> discord.Embed:
        return discord.Embed(
            color=discord.Color.dark_purple(),
        ).set_image(url=self._localization_image[self.locale])

    async def _delete_previous_message(self):
        last_message_id = self._redis.get(self.last_message_redis_key)
        if not last_message_id:
            return
        last_message_id = int(last_message_id)

        try:
            message = await self.channel.fetch_message(last_message_id)
        except discord.HTTPException as ex:
            sentry_sdk.capture_exception(ex)
            logger.warning(exc_info=ex)
            return

        try:
            await message.delete(delay=5)
        except discord.HTTPException as ex:
            sentry_sdk.capture_exception(ex)
            logger.warning(exc_info=ex)
