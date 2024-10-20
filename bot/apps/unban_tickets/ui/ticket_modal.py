from discord import Interaction

from bot.apps.unban_tickets.actions.create_unban_ticket import CreateUnbanTicket
from bot.apps.unban_tickets.errors import UnbanTicketError
from core.localization import LocaleEnum
from core.ui.modals import BaseLocalizationModal, InputText


class CreateTicketModal(BaseLocalizationModal):
    steam_id = InputText(
        label='SteamID',
        placeholder='76561199999999999',
        min_length=17,
    )
    reason = InputText(
        placeholder='Читы/Игра 1+/...',
    )

    inputs_localization_map = {
        reason: {
            LocaleEnum.ru: dict(label='Причина блокировки'),
            LocaleEnum.en: dict(label='Ban reason'),
        }
    }

    title_localization_map = {
        LocaleEnum.ru: 'Заявка на разбан',
        LocaleEnum.en: 'Unban request',
    }

    response_localization = {
        LocaleEnum.ru: 'Ваша заявка отправлена. '
        'Результат будет отправлен вам в личные сообщения с ботом, убедитесь что вы не закрыли доступ.',
        LocaleEnum.en: 'Your request has been sent. '
        'The result will be sent to you in private messages with the bot, make sure you have not locked access.',
    }

    async def callback(self, interaction: Interaction):
        await CreateUnbanTicket(
            guild=interaction.guild,
            user=interaction.user,
            steam_id=self.steam_id,
            reason=self.reason,
            locale=self.locale,
        ).execute()

        response = self.response_localization[self.locale]
        await interaction.respond(response, ephemeral=True)

    async def on_error(self, error: Exception, interaction: Interaction) -> None:
        if isinstance(error, UnbanTicketError):
            return await interaction.respond(error.message, ephemeral=True, delete_after=30)
        return await super().on_error(error, interaction)
