import discord

from core.api_clients.magic_rust import MagicRustServerDataAPI
from core.localization import LocaleEnum, LocalizationDict


class FindServerButton(discord.ui.Button):
    label_localization = LocalizationDict(
        {
            LocaleEnum.en: 'Find server',
            LocaleEnum.ru: 'Подобрать сервер',
        }
    )

    def __init__(self, locale: LocaleEnum):
        self.locale = locale
        super().__init__(
            style=discord.ButtonStyle.primary,
            custom_id=f'server_filter:{locale}:button:send_filter',
            label=self.label_localization[locale],
        )

    async def callback(self, interaction: discord.Interaction):
        from bot.apps.server_status.views import ServerFilterView

        server_data = await MagicRustServerDataAPI().get_server_data()
        await interaction.response.send_message(
            view=ServerFilterView(locale=self.locale, server_data=server_data),
            ephemeral=True,
        )
