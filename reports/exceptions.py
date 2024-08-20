from discord.ext.commands.errors import CommandError

from core.localization import LocaleEnum


class ReportsError(CommandError):
    message: str


class UserReportCooldownError(ReportsError):
    locale_map: dict[LocaleEnum, str] = {
        LocaleEnum.en: 'You recently sent in a report. Please wait <t:{}:R>',
        LocaleEnum.ru: 'Вы недавно отправляли жалобу. Повторите попытку через <t:{}:R>',
    }

    def __init__(self, cooldown_end_timestamp: float, locale: LocaleEnum):
        self.message = self.locale_map[locale].format(int(cooldown_end_timestamp))
