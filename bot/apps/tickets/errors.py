from discord.ext.commands import CommandError

from core.localization import LocaleEnum


class TicketError(CommandError):
    message: str

    def __init__(self):
        super().__init__(self.message)


class UserAlreadyHaveTicket(TicketError):
    message_localization = {
        LocaleEnum.ru: 'У вас уже открыт тикет: {ticket_channel_mention}',
        LocaleEnum.en: 'You already have a ticket open: {ticket_channel_mention}',
    }

    def __init__(self, locale: LocaleEnum, ticket_channel_mention: str):
        message = self.message_localization[locale].format(ticket_channel_mention=ticket_channel_mention)
        self.message = message
        super().__init__()


class NoTicketFound(TicketError):
    message = 'Тикета в выбранном канале не найдено'


class ActionAllowOnlyForTicketAuthorError(TicketError):
    message = 'Действие доступно только для автора тикета'
