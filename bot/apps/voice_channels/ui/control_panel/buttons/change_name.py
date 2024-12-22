import discord
from discord import Interaction

from bot.apps.voice_channels.actions import ChangeNameAction
from bot.apps.voice_channels.ui.control_panel.permissions import check_panel_access
from bot.custom_emoji import CustomEmojis
from core.localization import LocaleEnum
from core.ui.modals import BaseLocalizationModal, InputText


class ChangeNameButton(discord.ui.Button):
    def __init__(self, locale: LocaleEnum, voice_channel: discord.VoiceChannel):
        self.locale = locale
        self.voice_channel = voice_channel
        super().__init__(
            style=discord.ButtonStyle.gray,
            custom_id=f'control-panel:{voice_channel.id}:button:change-name',
            emoji=CustomEmojis.CHANGE_NAME,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        await check_panel_access(self.voice_channel, interaction.user)

        modal = ChangeNameModal(
            locale=self.locale,
            voice_channel=self.voice_channel,
        )
        await interaction.response.send_modal(modal)


class ChangeNameModal(BaseLocalizationModal):
    title_localization_map = {
        LocaleEnum.ru: 'Изменить названия канала',
        LocaleEnum.en: 'Change name',
    }

    new_name = InputText(
        max_length=40,
    )

    inputs_localization_map = {
        new_name: {
            LocaleEnum.ru: {'label': 'Новое название'},
            LocaleEnum.en: {'label': 'New channel name'},
        }
    }

    response_localization_map = {
        LocaleEnum.ru: 'Название канала изменено {new_name}',
        LocaleEnum.en: 'New channel name {new_name}',
    }

    def __init__(self, *args, voice_channel: discord.VoiceChannel, **kwargs):
        super().__init__(*args, **kwargs)
        self.voice_channel = voice_channel

    async def callback(self, interaction: Interaction):
        await ChangeNameAction(
            self.voice_channel,
            self.new_name,
        ).execute()

        await interaction.respond(
            self.response_localization_map[self.locale].format(new_name=self.new_name),
            ephemeral=True,
            delete_after=15,
        )
