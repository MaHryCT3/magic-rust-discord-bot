import datetime
from typing import Final, Iterable

import discord
from dateutil.rrule import HOURLY, MINUTELY, rrule

from bot.apps.bot_messages.exceptions import SendTimeInPastError, SendTimeParseError
from bot.config import settings
from bot.constants import DATETIME_FORMAT, TIME_FORMAT
from bot.core.utils.date_time import add_timezone_info
from bot.core.utils.math import round_to_value

SUGGESTION_COUNT: Final[int] = 10
MAX_DATE_INDEX: Final[int] = 10

# ну да тут жесткий навал говна


def parse_autocomplete_time(raw_time: str) -> datetime.datetime | None:
    if not raw_time:
        return None
    try:
        date_time = _parse_complete_time(raw_time)
    except Exception as e:
        raise SendTimeParseError() from e
    if datetime.datetime.now(tz=settings.TIMEZONE) > date_time:
        raise SendTimeInPastError()

    return date_time


def _parse_complete_time(raw_time: str) -> datetime.datetime:
    if '.' in raw_time:
        dt = datetime.datetime.strptime(raw_time, DATETIME_FORMAT)
        dt = add_timezone_info(dt, settings.TIMEZONE)
        return dt

    hour, minute = raw_time.split(':')
    hour, minute = int(hour), int(minute)
    return datetime.datetime.combine(
        datetime.datetime.now(tz=settings.TIMEZONE).date(),
        datetime.time(hour, minute),
        tzinfo=settings.TIMEZONE,
    )


def select_time_autocomplete(ctx: discord.AutocompleteContext) -> list[str]:
    results = _select_time_autocomplete(ctx)
    return [_format_result(result) for result in results]


def _select_time_autocomplete(ctx: discord.AutocompleteContext) -> Iterable[datetime.datetime | datetime.time]:
    ctx.value = ctx.value.strip()
    if not ctx.value:
        return _default_time_select()

    day, month, year, hour, minute = None, None, None, None, None
    try:
        if '.' in ctx.value:
            dates_units = ctx.value[:MAX_DATE_INDEX].split('.', maxsplit=2)
            dates_units = [int(unit) for unit in dates_units if unit]
            if len(dates_units) == 1:
                day = int(dates_units[0])
            if len(dates_units) == 2:  # noqa: PLR2004
                day, month = dates_units
            if len(dates_units) == 3:  # noqa: PLR2004
                day, month, year = dates_units

        # day none if passed only time, year not none if passed full date
        if day is None or (year is not None and len(ctx.value) > MAX_DATE_INDEX):
            # we parsed (10.05.23) part of 10.05.23 12:12
            # cut to 12:12
            start_index = MAX_DATE_INDEX if year else 0
            times = ctx.value[start_index:]
            hour, minute = times.split(':', maxsplit=1) if ':' in times else (times, None)
            hour = int(hour)
            minute = int(minute) if minute else None
        return _get_select_time_suggestions(day, month, year, hour, minute)

    except (ValueError, TypeError):
        return _default_time_select()


def _format_result(d: datetime.datetime | datetime.time) -> str:
    if isinstance(d, datetime.datetime):
        return d.strftime(DATETIME_FORMAT)
    if isinstance(d, datetime.time):
        return d.strftime(TIME_FORMAT)


def _default_time_select() -> Iterable[datetime.datetime]:
    date_time = datetime.datetime.now(tz=settings.TIMEZONE) + datetime.timedelta(hours=1)
    date_time = date_time.replace(minute=0)
    date_times = rrule(
        dtstart=date_time,
        count=SUGGESTION_COUNT,
        freq=HOURLY,
    )
    return date_times


def _get_select_time_suggestions(
    day: int | None = None,
    month: int | None = None,
    year: int | None = None,
    hour: int | None = None,
    minute: int | None = None,
) -> Iterable[datetime.datetime | datetime.time]:
    now = datetime.datetime.now()
    if hour is not None:
        time = datetime.time(hour, minute or 0)
    else:
        time = now.time()

    # округляем до 10
    rounded_to_next_10 = round_to_value(time.minute, 10)
    rounded_to_next_10 = 0 if rounded_to_next_10 == 60 else rounded_to_next_10  # noqa: PLR2004
    time = time.replace(minute=rounded_to_next_10)

    if not any([day, month, year]):
        return _get_times_suggestions(time)

    replaced_now = now.replace()
    if day:
        replaced_now = replaced_now.replace(day=day)
    if month:
        replaced_now = replaced_now.replace(month=month)
    if year:
        replaced_now = replaced_now.replace(year=year)

    date = replaced_now.date()
    return _get_datetimes_suggestion(datetime.datetime.combine(date, time))


def _get_times_suggestions(time: datetime.time) -> Iterable[datetime.time]:
    results: Iterable[datetime.datetime] = rrule(
        dtstart=datetime.datetime.combine(date=datetime.date.today(), time=time),
        freq=MINUTELY,
        count=SUGGESTION_COUNT,
        byminute=[0, 10, 20, 30, 40, 50],
    )
    return [result.time() for result in results]


def _get_datetimes_suggestion(date_time: datetime.datetime) -> Iterable[datetime.datetime]:
    results: Iterable[datetime.datetime] = rrule(
        dtstart=date_time,
        until=date_time + datetime.timedelta(hours=SUGGESTION_COUNT),
        freq=HOURLY,
    )
    return results
