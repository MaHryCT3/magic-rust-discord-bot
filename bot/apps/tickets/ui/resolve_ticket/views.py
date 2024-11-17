import discord
from discord import Interaction
from discord.ui import Item

from bot.apps.tickets.actions.no_resolve_ticket import NoResolveTicketAction
from bot.apps.tickets.actions.resolve_ticket import ResolveTicketAction
from bot.apps.tickets.errors import TicketError
from core.localization import LocaleEnum


class ResolveTicketView(discord.ui.View):
    resolve_label_localization = {
        LocaleEnum.ru: 'Вопрос решен',
        LocaleEnum.en: 'Issue resolved',
    }

    no_resolve_label_localization = {
        LocaleEnum.ru: 'Ответ не получен',
        LocaleEnum.en: 'No answer received',
    }

    def __init__(self, locale: LocaleEnum):
        self.locale = locale

        resolve_ticket_button = discord.ui.Button(
            style=discord.ButtonStyle.green,
            label=self.resolve_label_localization[self.locale],
            custom_id=f'resolve_ticket:{self.locale}:button:resolve',
        )
        resolve_ticket_button.callback = self._resolve_button_callback

        no_resolve_button = discord.ui.Button(
            style=discord.ButtonStyle.red,
            label=self.no_resolve_label_localization[self.locale],
            custom_id=f'resolve_ticket:{self.locale}:button:no_resolve',
        )
        no_resolve_button.callback = self._no_resolve_button_callback

        super().__init__(
            resolve_ticket_button,
            no_resolve_button,
            timeout=None,
        )

    async def _resolve_button_callback(self, interaction: discord.Interaction) -> None:
        action = ResolveTicketAction(
            channel=interaction.channel,
            resolve_by=interaction.user,
            message=interaction.message,
        )
        await action.execute()
        await interaction.response.edit_message(view=None)

    async def _no_resolve_button_callback(self, interaction: discord.Interaction) -> None:
        action = NoResolveTicketAction(
            channel=interaction.channel,
            resolve_by=interaction.user,
            message=interaction.message,
        )
        await action.execute()
        await interaction.response.edit_message(view=None)

    async def on_error(self, error: Exception, item: Item, interaction: Interaction):
        if isinstance(error, TicketError):
            return await interaction.respond(error.message, ephemeral=True)
        return super().on_error(error, item, interaction)
