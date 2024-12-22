import discord

from bot.apps.voice_channels.actions import SetRoomLimitAction
from bot.apps.voice_channels.ui.control_panel.permissions import check_panel_access
from bot.custom_emoji import CustomEmojis
from core.localization import LocaleEnum


class SetRoomLimitButton(discord.ui.Button):
    def __init__(self, locale: LocaleEnum, voice_channel: discord.VoiceChannel):
        self.locale = locale
        self.voice_channel = voice_channel
        super().__init__(
            style=discord.ButtonStyle.gray,
            custom_id=f'control-panel:{voice_channel.id}:button:limit',
            emoji=CustomEmojis.LIMIT,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        await check_panel_access(self.voice_channel, interaction.user)

        await interaction.response.send_message(
            view=SetRoomLimitView(
                locale=self.locale,
                voice_channel=self.voice_channel,
            ),
            ephemeral=True,
            delete_after=20,
        )


class SetRoomLimitView(discord.ui.View):
    placeholder_localization = {
        LocaleEnum.ru: 'Выбрать лимит',
        LocaleEnum.en: 'Select limit',
    }

    answer_localization = {
        LocaleEnum.ru: 'Лимит установлен на {limit}',
        LocaleEnum.en: 'Limit is set to {limit}',
    }

    def __init__(
        self,
        locale: LocaleEnum,
        voice_channel: discord.VoiceChannel,
    ):
        self.locale = locale
        self.voice_channel = voice_channel

        self._limit_select = discord.ui.Select(
            placeholder=self.placeholder_localization[self.locale],
            options=[
                discord.SelectOption(
                    label=str(limit + 1),
                )
                for limit in range(20)
            ],
        )
        self._limit_select.callback = self._limit_select_callback

        super().__init__(self._limit_select)

    async def _limit_select_callback(self, interaction: discord.Interaction):
        limit = int(self._limit_select.values[0])
        await SetRoomLimitAction(
            voice_channel=self.voice_channel,
            limit=limit,
        ).execute()

        await interaction.respond(
            self.answer_localization[self.locale].format(limit=limit),
            ephemeral=True,
            delete_after=15,
        )
