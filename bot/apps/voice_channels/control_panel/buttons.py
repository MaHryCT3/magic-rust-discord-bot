import discord

from bot.apps.voice_channels.control_panel.embeds import (
    InsufficientPermissionsEmbed,
    KickEmbed,
)
from core.emojis import Emojis
from core.localization import LocaleEnum, LocalizationDict


class KickButton(discord.ui.Button):
    label_localization = LocalizationDict(
        {
            LocaleEnum.en: ' Kick',
            LocaleEnum.ru: ' Выгнать',
        }
    )

    def __init__(self, locale: LocaleEnum, voice_channel: discord.VoiceChannel):
        self.locale = locale
        self.voice_channel = voice_channel
        super().__init__(
            style=discord.ButtonStyle.primary,
            custom_id=f'control-panel:{voice_channel.id}:button:kick',
            emoji=Emojis.DIZZY,
            label=self.label_localization[locale],
        )

    async def callback(self, interaction: discord.Interaction):
        if not self.voice_channel.permissions_for(interaction.user).manage_channels:
            await interaction.response.send_message(
                embed=InsufficientPermissionsEmbed.build(self.locale), ephemeral=True
            )
            return
        from bot.apps.voice_channels.control_panel.views import KickView

        members = (await interaction.guild.fetch_channel(self.voice_channel.id)).members
        members_except_managers = [
            member for member in members if not self.voice_channel.permissions_for(member).manage_channels
        ]
        await interaction.response.send_message(
            view=KickView(locale=self.locale, members=members_except_managers, voice_channel=self.voice_channel),
            embed=KickEmbed.build(self.locale),
            ephemeral=True,
            delete_after=20,
        )
