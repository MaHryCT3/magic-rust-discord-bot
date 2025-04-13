import discord

from bot.constants import MAIN_COLOR
from core.emojis import Emojis
from core.localization import LocaleEnum


class ReviewEmbed(discord.Embed):
    score_localization = {
        LocaleEnum.ru: f'{Emojis.STAR}Оценка',
        LocaleEnum.en: f'{Emojis.STAR}Score',
    }

    review_localization = {
        LocaleEnum.ru: f'{Emojis.MESSAGE}Отзыв',
        LocaleEnum.en: f'{Emojis.MESSAGE}Review',
    }

    @classmethod
    def build(
        cls,
        locale: LocaleEnum,
        score: int,
        review: str | None = None,
    ):
        embed = cls(color=MAIN_COLOR)
        embed.add_field(
            name=cls.score_localization[locale],
            value=str(score),
        )

        if review:
            embed.add_field(
                name=cls.review_localization[locale],
                value=review,
            )
        return embed
