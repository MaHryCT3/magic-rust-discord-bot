import discord
from discord import Interaction

from bot.apps.servicing_posts.services.models import (
    ServicingActionEnum,
    ServicingPostSettings,
)
from bot.apps.servicing_posts.services.settings import ServicingPostsSettingsService
from core.emojis import Emojis
from core.localization import LocaleEnum
from core.utils.format_strings import mention_channel

emoji_by_action = {
    ServicingActionEnum.LIKE: Emojis.LIKE,
    ServicingActionEnum.DISLIKE: Emojis.DISLIKE,
    ServicingActionEnum.THREADS: Emojis.MESSAGE,
}


class SelectServicingActionSelect(discord.ui.Select):
    def __init__(
        self,
        channel_id: int,
        channel_name: str,
        locale: LocaleEnum,
        servicing_posts_settings: ServicingPostsSettingsService,
        selected_actions: list[ServicingActionEnum] | None = None,
    ):
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.locale = locale
        self.servicing_posts_settings = servicing_posts_settings
        self.selected_actions = selected_actions
        super().__init__(
            placeholder=f'Выберите настройки для канала {self.channel_name}',
            max_values=len(ServicingActionEnum),
            options=[
                discord.SelectOption(
                    label=action.value,
                    default=action in selected_actions if selected_actions else False,
                    emoji=emoji_by_action.get(action),
                )
                for action in ServicingActionEnum
            ],
        )

    async def callback(self, interaction: Interaction):
        actions = self._get_selects_actions()
        setting = self._to_setting(actions)
        await self.servicing_posts_settings.add_setting(setting)

        actions_str = ', '.join([action.value for action in actions])
        await interaction.respond(
            f'{mention_channel(self.channel_id)} добавлен в обслуживание. Со следующими настройками: {actions_str}',
            ephemeral=True,
            delete_after=10,
        )

    def _get_selects_actions(self) -> set[ServicingActionEnum]:
        return {ServicingActionEnum(value) for value in self.values}

    def _to_setting(self, actions: set[ServicingActionEnum]) -> ServicingPostSettings:
        return ServicingPostSettings(
            channel_id=self.channel_id,
            channel_name=self.channel_name,
            locale=self.locale,
            add_like=ServicingActionEnum.LIKE in actions,
            add_dislike=ServicingActionEnum.DISLIKE in actions,
            add_threads=ServicingActionEnum.THREADS in actions,
            ignore_bot=ServicingActionEnum.IGNORE_BOT in actions,
            remove_bot_msg=ServicingActionEnum.REMOVE_BOT in actions,
        )
