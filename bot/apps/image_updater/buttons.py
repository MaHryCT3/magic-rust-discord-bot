import discord

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
        from bot.apps.image_updater.views import ServerFilterView

        await interaction.response.send_message(view=ServerFilterView(locale=self.locale), ephemeral=True)
