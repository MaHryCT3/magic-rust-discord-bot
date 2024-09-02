from discord.ext.commands.errors import CommandError

from core.localization import LocaleEnum
from core.utils.humanize import human_time


class BaseFindFriendsError(CommandError):
    message: str


class UserOnCooldownError(BaseFindFriendsError):
    locale_map = {
        LocaleEnum.en: 'You can submit a friend request once per {cooldown}. You have to wait for {retry_after}.',
        LocaleEnum.ru: 'Отправлять заявку на поиск друга можно раз в {cooldown}. Осталось подождать {retry_after}.',
    }

    def __init__(self, cooldown: float, retry_after: float, locale: LocaleEnum):
        self.cooldown = cooldown
        self.retry_after = retry_after

        # TODO: Изменить на дискордовское время
        human_cooldown = human_time(int(self.cooldown), locale)
        human_retry_after = human_time(int(self.retry_after), locale)

        message_template = self.locale_map[locale]
        self.message = message_template.format(cooldown=human_cooldown, retry_after=human_retry_after)


class CommandNotConfiguredError(BaseFindFriendsError):
    locale_map = {
        LocaleEnum.en: 'The command is not configured. Contact your administrator.',
        LocaleEnum.ru: 'Команда не настроена. Обратитесь к администратору.',
    }

    def __init__(self, locale: LocaleEnum):
        self.message = self.locale_map[locale]
