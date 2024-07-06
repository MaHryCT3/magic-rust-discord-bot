from discord import Interaction

from bot.core.localization import LocaleEnum
from bot.core.redis_cooldown import RedisLocaleCooldown
from bot.core.ui.modals import BaseLocalizationModal, InputText
from bot.dynamic_settings import DynamicSettings


class FindFriendModal(BaseLocalizationModal):
    article = InputText(
        label='Заголовок',
        placeholder='place',
        max_length=50,
    )

    localization_map = {
        article: {
            LocaleEnum.en: dict(label='Article', placeholder='find friend', value='friend find'),
        }
    }

    def __init__(self, redis_cooldown: RedisLocaleCooldown, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_cooldown = redis_cooldown

    async def callback(self, interaction: Interaction):
        if await self.redis_cooldown.is_user_on_cooldown(interaction.user.id, self.locale):
            raise

        await interaction.response.send_message(self.article, ephemeral=True)
        await self.redis_cooldown.set_user_cooldown(
            user_id=interaction.user.id,
            locale=self.locale,
            cooldown_in_seconds=DynamicSettings().find_friend_cooldown,
        )
