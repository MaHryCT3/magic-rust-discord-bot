import discord

from bot.apps.voice_channels.control_panel.buttons import KickButton
from bot.apps.voice_channels.control_panel.select_buttons import MemberKickSelect
from core.localization import LocaleEnum


class ControlPanelView(discord.ui.View):
    def __init__(
        self,
        locale: LocaleEnum,
        voice_channel: discord.VoiceChannel,
    ):
        self.locale = locale
        kick_button = KickButton(locale, voice_channel)
        super().__init__(kick_button, timeout=None)


class KickView(discord.ui.View):
    def __init__(self, locale: LocaleEnum, members: list[discord.Member], voice_channel: discord.VoiceChannel):
        self.locale = locale
        self.member_kick_select = MemberKickSelect.build(
            locale=locale, voice_members=members, voice_channel=voice_channel
        )

        super().__init__(self.member_kick_select, timeout=None)
