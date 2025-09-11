import datetime

from discord.ext.commands import CommandError


class ExporterError(CommandError): ...


class ExporterDateInvalidFormat(ExporterError):
    def __init__(self, date_format: str):
        super().__init__(f'Некорректно введена дата, формат ввода: {date_format}')


class DateToLessThanDateFrom(ExporterError):
    def __init__(self, date_from: datetime.datetime, date_to: datetime.datetime):
        message = (
            f"Проверьте даты: период с {date_from.strftime('%d.%m.%Y')} по {date_to.strftime('%d.%m.%Y')} невозможен."
        )
        super().__init__(message)
