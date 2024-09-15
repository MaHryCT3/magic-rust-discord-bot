from core.localization import LocaleEnum


class RoomCreateCooldownError(Exception):
    def __init__(self, cooldown: float, retry_after: float, locale: LocaleEnum):
        self.cooldown = cooldown
        self.retry_after = retry_after
        self.locale = locale


class CategoryNotConfiguredError(Exception):
    pass
