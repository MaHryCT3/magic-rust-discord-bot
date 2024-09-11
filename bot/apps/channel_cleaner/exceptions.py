from bot.apps.channel_cleaner.embeds import RoomCreationCooldownEmbed
from core.localization import LocaleEnum


class RoomCreateCooldownError(Exception):
    def __init__(self, cooldown: float, retry_after: float, locale: LocaleEnum):
        self.cooldown = cooldown
        self.retry_after = retry_after
        self.locale = locale

    def get_embed(self) -> RoomCreationCooldownEmbed:
        return RoomCreationCooldownEmbed.build(int(self.cooldown), int(self.retry_after), self.locale)


class CategoryNotConfiguredError(Exception):
    pass
