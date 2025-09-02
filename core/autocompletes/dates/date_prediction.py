import datetime
from typing import Callable

import discord

from bot.constants import DATE_FORMAT
from core.autocompletes.base import BaseAutocomplete
from core.autocompletes.dates.date_args import PredictionDate


class DatePredictionAutocomplete(BaseAutocomplete):

    def __init__(
        self,
        default_date_getter: Callable[[], list[datetime.date]] | None = None,
    ):
        self._default_date_getter = default_date_getter
        self._date_format = DATE_FORMAT

    def autocomplete(self, ctx: discord.AutocompleteContext) -> list[str]:
        value = ctx.value.strip()
        if not value and self._default_date_getter:
            date = self._default_date_getter()

        elif not value:
            return []
        else:
            date = PredictionDate(value).get_prediction()

        return [date.strftime(self._date_format)]
