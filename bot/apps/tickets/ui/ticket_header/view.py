import discord

from bot.apps.tickets.actions.close_ticket import CloseTicketAction
from core.emojis import Emojis
from core.localization import LocaleEnum


class TicketHeaderView(discord.ui.View):
    close_ticket_button_localization = {
        LocaleEnum.ru: 'Закрыть обращение',
        LocaleEnum.en: 'Close ticket',
    }

    def __init__(self, locale: LocaleEnum, **kwargs):
        self.locale = locale
        kwargs.setdefault('timeout', None)
        super().__init__(**kwargs)

        close_ticket_button = discord.ui.Button(
            label=self.close_ticket_button_localization[self.locale],
            emoji=Emojis.TICKET,
            custom_id=f'ticket_header:{self.locale}:button:close',
        )
        close_ticket_button.callback = self.close_ticket_button_callback

        self.add_item(close_ticket_button)

    async def close_ticket_button_callback(self, interaction: discord.Interaction):
        self.disable_all_items()
        await interaction.response.edit_message(view=self)

        await CloseTicketAction(interaction.channel, interaction.user).execute()
