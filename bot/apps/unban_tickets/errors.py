import discord

from bot.apps.unban_tickets.services.unban_tickets import UnbanTicketStruct
from core.errors.base import BaseDiscordError
from core.localization import LocaleEnum
from core.utils.format_strings import format_relative_time, mention_user


class UnbanTicketError(BaseDiscordError):
    pass


class UnbanTicketCooldownError(UnbanTicketError):
    message_localization: dict[LocaleEnum, str] = {
        LocaleEnum.ru: 'Вы уже недавно создавали заявку на разбан. Следующий раз вы сможете это сделать через {}',
        LocaleEnum.en: 'You have already recently created an unban ticket. Try again in a {}',
    }

    @property
    def message(self) -> str:
        relative_time = format_relative_time(int(self.retry_after))
        return self.message_localization[self.locale].format(relative_time)

    def __init__(
        self,
        retry_after: float,
        locale: LocaleEnum,
    ):
        self.retry_after = retry_after
        self.locale = locale
        super().__init__()


class AlreadyHaveUnbanTicketError(UnbanTicketError):
    message_localization: dict[LocaleEnum, str] = {
        LocaleEnum.ru: 'У вас есть не рассмотренная заявка на разбан',
        LocaleEnum.en: 'You have a pending unban ticket',
    }

    @property
    def message(self):
        return self.message_localization[self.ticket.locale]

    def __init__(self, user: discord.User, ticket: UnbanTicketStruct):
        self.ticket = ticket
        self.user = user
        super().__init__()


class UserDmIsClosed(UnbanTicketError):
    message_localization: dict[LocaleEnum, str] = {
        LocaleEnum.ru: 'Чтобы оставить заявку на разбан Вам нужно открыть личные сообщения для бота {bot_mention}',
        LocaleEnum.en: 'To leave an unban ticket you need to open private messages for the bot {bot_mention}',
    }

    @property
    def message(self) -> str:
        assert self.user and self.bot_id and self.locale, 'Нельзя использовать `message` без параметров'

        bot_mention = mention_user(self.bot_id)
        return self.message_localization[self.locale].format(bot_mention=bot_mention)

    def __init__(self, user: discord.User | None = None, bot_id: int | None = None, locale: LocaleEnum | None = None):
        self.user = user
        self.bot_id = bot_id
        self.locale = locale


class SteamIDIsNotValid(UnbanTicketError):
    message_localization: dict[LocaleEnum, str] = {
        LocaleEnum.ru: 'Вы ввели неверный стим, попробуйте еще раз',
        LocaleEnum.en: 'You entered the wrong steam, try again.',
    }

    @property
    def message(self) -> str:
        return self.message_localization[self.locale]

    def __init__(self, locale: LocaleEnum):
        self.locale = locale


class UserDontHaveTicket(BaseDiscordError):
    pass
