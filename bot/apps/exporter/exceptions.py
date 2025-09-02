class ExporterError(Exception): ...


class ExporterDateInvalidFormat(ExporterError):
    def __init__(self, date_format: str):
        super().__init__(f'Некорректно введена дата, формат ввода: {date_format}')
