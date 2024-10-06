from discord.ext.commands import CommandError

from core.localization import LocaleEnum


class TicketError(CommandError):
    message: str


class UserAlreadyHaveTicket(TicketError):
    message_localization = {
        LocaleEnum.ru: 'У вас уже открыт тикет: {ticket_channel_mention}',
        LocaleEnum.en: 'You already have a ticket open: {ticket_channel_mention}}',
    }

    def __init__(self, locale: LocaleEnum, ticket_channel_mention: str):
        message = self.message_localization[locale].format(ticket_channel_mention=ticket_channel_mention)
        super().__init__(message)
        self.message = message
