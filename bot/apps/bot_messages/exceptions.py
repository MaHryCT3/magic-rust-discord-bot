from discord.ext.commands.errors import CommandError


class BotMessageError(CommandError):
    message: str


class SendTimeParseError(BotMessageError):
    message: str = 'Ошибка парсинга времени отправки сообщения. Доступный формат: "14:00" или "08.07.2024 12:39"'


class SendTimeInPastError(BotMessageError):
    message: str = 'Нельзя сделать отложенное сообщение в прошлое'


class QueueMessageIsEmpty(BotMessageError):
    message: str = 'Очередь сообщений пуста'
