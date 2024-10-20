import discord

from bot.apps.unban_tickets.actions.send_unban_ticket_modal import SendUnbanTicketModal
from bot.apps.unban_tickets.errors import UnbanTicketError
from core.emojis import Emojis
from core.localization import LocaleEnum


class CreateUnbanTicketView(discord.ui.View):
    unban_button_localization = {
        LocaleEnum.ru: 'Создать заявку',
        LocaleEnum.en: 'Create unban request',
    }

    def __init__(self, locale: LocaleEnum):
        self.locale = locale

        unban_button = discord.ui.Button(
            label=self.unban_button_localization[self.locale],
            emoji=Emojis.TICKET,
            custom_id=f'unban_ticket:{self.locale}:button:create',
        )
        unban_button.callback = self.create_ticket_button_callback

        super().__init__(unban_button, timeout=None)

    async def create_ticket_button_callback(self, interaction: discord.Interaction):
        await SendUnbanTicketModal(self.locale, interaction).execute()

    @classmethod
    def all_locales_init(cls):
        return [cls(locale) for locale in LocaleEnum]

    async def on_error(self, exception: Exception, item: discord.ui.Item, interaction: discord.Interaction) -> None:
        if isinstance(exception, UnbanTicketError):
            return await interaction.respond(exception.message, ephemeral=True, delete_after=30)
        return await super().on_error(exception, item, interaction)
