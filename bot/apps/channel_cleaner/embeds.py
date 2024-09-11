from time import time
from typing import Self

import discord

from core.localization import LocaleEnum, LocalizationDict
from core.utils.colors import WARNING_YELLOW


class RoomCreationCooldownEmbed(discord.Embed):
    title_localization = LocalizationDict(
        {LocaleEnum.en: ':hourglass_flowing_sand: Chill!', LocaleEnum.ru: ':hourglass_flowing_sand: Остыньте!'}
    )
    message_localization = LocalizationDict(
        {
            LocaleEnum.en: "You can create voice channels once in `{cooldown}` seconds. You'll be able to create <t:{retry_after_stamp}:R`.",
            LocaleEnum.ru: 'Голосовой канал можно создавать каждые `{cooldown}` секунд. Вы сможете создать <t:{retry_after_stamp}:R>.',
        }
    )

    @classmethod
    def build(cls, cooldown: int, retry_after: int, locale: LocaleEnum) -> Self:
        retry_after_stamp = int(time() + retry_after) + 1
        embed = cls(color=WARNING_YELLOW)
        embed.title = cls.title_localization[locale]
        embed.description = cls.message_localization[locale].format(
            cooldown=cooldown, retry_after_stamp=retry_after_stamp
        )
        return embed
