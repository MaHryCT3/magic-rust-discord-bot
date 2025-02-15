import datetime

import discord
from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, MO, MONTHLY, rrule

from bot.apps.voice_activity.ui.activity_stats.enum import ActivityPeriodTypeEnum
from core.localization import LocaleEnum, month_name
from core.utils.date_time import get_last_day_of_month, get_next_sunday


class PeriodSelectService:
    # лимит дискорда
    MAX_OPTIONS: int = 25
    # дата ввода функционала, больше данных нет
    MAX_DATE: datetime.date = datetime.date(2025, 2, 1)

    def __init__(self, locale: LocaleEnum, period_type: ActivityPeriodTypeEnum):
        self.locale = locale
        self.period_type = period_type

    def get_available_options(self, default_value: str | None = None) -> list[discord.SelectOption]:
        if self.period_type == ActivityPeriodTypeEnum.MONTH:
            selects = self._get_month_selects()
        elif self.period_type == ActivityPeriodTypeEnum.WEEK:
            selects = self._get_weeks_selects()
        elif self.period_type == ActivityPeriodTypeEnum.DAYS:
            selects = self._get_day_selects()
        else:
            raise TypeError(f'Неизвестный тип {self.period_type}')

        if not selects:
            return selects

        is_default_set = False
        if default_value:
            for select in selects:
                if select.value == default_value:
                    select.default = True
                    is_default_set = True
                    break

        if not is_default_set:
            selects[0].default = True

        return selects

    def get_time_period_by_select(self, selected_value: str) -> tuple[datetime.date, datetime.date]:
        date = datetime.datetime.fromisoformat(selected_value).date()
        if self.period_type == ActivityPeriodTypeEnum.MONTH:
            return date, date + relativedelta(months=1)
        if self.period_type == ActivityPeriodTypeEnum.WEEK:
            return date, date + datetime.timedelta(days=7)
        if self.period_type == ActivityPeriodTypeEnum.DAYS:
            return date, date + datetime.timedelta(days=1)
        raise TypeError(f'Неизвестный тип {self.period_type}')

    def get_default_period(self):
        options = self.get_available_options()
        for option in options:
            if option.default:
                return self.get_time_period_by_select(option.value)

    def _get_month_selects(self) -> list[discord.SelectOption]:
        months_times = self._get_month_iterator()
        return [
            discord.SelectOption(
                label=self._get_month_label(month_date),
                value=month_date.isoformat(),
            )
            for month_date in months_times
        ]

    def _get_month_iterator(self) -> list[datetime.datetime]:
        iterator = rrule(
            MONTHLY,
            dtstart=self.MAX_DATE,
            until=get_last_day_of_month(),
        )
        return list(iterator)[::-1][: self.MAX_OPTIONS]

    def _get_month_label(self, month: datetime.datetime):
        month_str = month_name(month.month, self.locale)
        return f'{month.year} {month_str}'

    def _get_weeks_selects(self):
        week_times = self._get_weeks_iterator()
        return [
            discord.SelectOption(
                label=self._get_week_label(week),
                value=week.isoformat(),
            )
            for week in week_times
        ]

    def _get_weeks_iterator(self) -> list[datetime.datetime]:
        iterator = rrule(
            DAILY,
            dtstart=self.MAX_DATE,
            byweekday=[MO],
            until=get_next_sunday(),
        )
        return list(iterator)[::-1][: self.MAX_OPTIONS]

    def _get_week_label(self, week: datetime.datetime) -> str:
        end_week = get_next_sunday(week)
        format_str = '%d.%m'
        return f'{week.strftime(format_str)} - {end_week.strftime(format_str)}'

    def _get_day_selects(self) -> list[discord.SelectOption]:
        days = list(
            rrule(
                DAILY,
                count=7,
                dtstart=datetime.date.today() - datetime.timedelta(days=6),
            )
        )[::-1]

        return [
            discord.SelectOption(
                label=day.strftime('%d.%m'),
                value=day.isoformat(),
            )
            for day in days
        ]
