import discord
from discord import Interaction

from bot.apps.servicing_posts.services.models import ServicingPostSettings
from bot.apps.servicing_posts.services.settings import ServicingPostsSettingsService
from bot.apps.servicing_posts.ui.select_services_actions import (
    SelectServicingActionSelect,
)
from core.utils.format_strings import mention_channel


class BaseSelectServicingChannel(discord.ui.Select):
    def __init__(
        self, servicing_setting_service: ServicingPostsSettingsService, channels_settings: list[ServicingPostSettings]
    ):
        self.servicing_setting_service = servicing_setting_service
        self.channels_settings = channels_settings
        self.channels_settings_by_id = {
            channel_setting.channel_id: channel_setting for channel_setting in self.channels_settings
        }
        super().__init__(
            placeholder='Выберите сервер',
            options=[
                discord.SelectOption(
                    label=channel_setting.channel_name,
                    value=str(channel_setting.channel_id),
                )
                for channel_setting in self.channels_settings
            ],
        )

    @property
    def selected_channel(self) -> ServicingPostSettings:
        channel_id = self.values[0]
        return self.channels_settings_by_id[int(channel_id)]


class ServicingEditChannelsSelect(BaseSelectServicingChannel):
    async def callback(self, interaction: Interaction):
        channel_settings = self.selected_channel
        select = SelectServicingActionSelect(
            channel_id=channel_settings.channel_id,
            channel_name=channel_settings.channel_name,
            locale=channel_settings.locale,
            servicing_posts_settings=self.servicing_setting_service,
            selected_actions=channel_settings.get_actions(),
        )
        view = discord.ui.View(select)
        await interaction.response.edit_message(
            view=view,
            delete_after=60,
        )


class ServicingDeleteChannelsSelect(BaseSelectServicingChannel):
    async def callback(self, interaction: Interaction):
        await self.servicing_setting_service.remove_setting(self.selected_channel.channel_id)
        await interaction.respond(
            f'{mention_channel(self.selected_channel.channel_id)} больше не обслуживается',
            ephemeral=True,
            delete_after=10,
        )
