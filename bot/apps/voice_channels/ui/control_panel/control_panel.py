import discord
from discord import Interaction
from discord.ui import Item

from bot.apps.voice_channels.exceptions import DontHaveAccessError
from bot.apps.voice_channels.ui.control_panel.buttons import (
    ChangeNameButton,
    KickButton,
    TransferRightsButton,
)
from bot.apps.voice_channels.ui.control_panel.buttons.close_room import CloseRoomButton
from bot.apps.voice_channels.ui.control_panel.buttons.open_room import OpenRoomButton
from bot.apps.voice_channels.ui.control_panel.buttons.set_room_limit import (
    SetRoomLimitButton,
)
from bot.apps.voice_channels.ui.control_panel.embeds import InsufficientPermissionsEmbed
from core.localization import LocaleEnum


class ControlPanelView(discord.ui.View):
    def __init__(
        self,
        locale: LocaleEnum,
        voice_channel: discord.VoiceChannel,
    ):
        self.locale = locale
        self.voice_channel = voice_channel

        super().__init__(
            SetRoomLimitButton(self.locale, self.voice_channel),
            CloseRoomButton(self.locale, self.voice_channel),
            OpenRoomButton(self.locale, self.voice_channel),
            ChangeNameButton(self.locale, self.voice_channel),
            TransferRightsButton(self.locale, self.voice_channel),
            KickButton(self.locale, self.voice_channel),
            timeout=None,
        )

    async def on_error(self, error: Exception, item: Item, interaction: Interaction) -> None:
        if isinstance(error, DontHaveAccessError):
            await interaction.response.send_message(
                embed=InsufficientPermissionsEmbed.build(self.locale),
                ephemeral=True,
                delete_after=20,
            )
            return
        return await super().on_error(error, item, interaction)
