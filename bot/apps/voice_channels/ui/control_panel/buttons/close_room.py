import discord
from discord import Interaction

from bot.apps.voice_channels.actions import CloseRoomAction
from bot.apps.voice_channels.ui.control_panel.permissions import check_panel_access
from bot.custom_emoji import CustomEmojis
from core.localization import LocaleEnum


class CloseRoomButton(discord.ui.Button):
    response_localization = {
        LocaleEnum.ru: 'Комната закрыта',
        LocaleEnum.en: 'Room closed',
    }

    def __init__(self, locale: LocaleEnum, voice_channel: discord.VoiceChannel):
        self.locale = locale
        self.voice_channel = voice_channel
        super().__init__(
            style=discord.ButtonStyle.gray,
            custom_id=f'control-panel:{voice_channel.id}:button:close',
            emoji=CustomEmojis.CLOSE_ROOM,
            row=0,
        )

    async def callback(self, interaction: Interaction):
        await check_panel_access(self.voice_channel, interaction.user)

        await CloseRoomAction(self.voice_channel, self.locale).execute()

        await interaction.respond(
            self.response_localization[self.locale],
            ephemeral=True,
            delete_after=10,
        )
