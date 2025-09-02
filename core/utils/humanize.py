from typing import Final, TypeAlias, TypedDict

from core.localization import LocaleEnum

ONE_HOUR_SECONDS: Final[int] = 3600
ONE_YEAR_SECONDS: Final[int] = 365 * 24 * 60 * 60
ONE_DAY_SECONDS = 24 * 60 * 60
ONE_MONTH_SECONDS: Final[int] = 30 * 24 * 60 * 60


WordForms: TypeAlias = tuple[str, str, str]


class TimeUnit(TypedDict):
    seconds: WordForms
    hours: WordForms
    minutes: WordForms
    days: WordForms
    months: WordForms
    years: WordForms


units_locale: dict[LocaleEnum, TimeUnit] = {
    LocaleEnum.en: TimeUnit(
        seconds=('second', 'second', 'seconds'),
        minutes=('minute', 'minute', 'minutes'),
        hours=('hour', 'hour', 'hours'),
        days=('day', 'day', 'days'),
        months=('month', 'month', 'months'),
        years=('year', 'year', 'years'),
    ),
    LocaleEnum.ru: TimeUnit(
        seconds=('секунда', 'секунды', 'секунд'),
        minutes=('минута', 'минуты', 'минут'),
        hours=('час', 'часа', 'часов'),
        days=('день', 'дня', 'дней'),
        months=('месяц', 'месяца', 'месяцев'),
        years=('год', 'года', 'лет'),
    ),
}

TIME_UNITS = [
    ('years', ONE_YEAR_SECONDS),
    ('months', ONE_MONTH_SECONDS),
    ('days', ONE_DAY_SECONDS),
    ('hours', ONE_HOUR_SECONDS),
    ('minutes', 60),
    ('seconds', 1),
]


def human_time(seconds: int, locale: LocaleEnum = LocaleEnum.ru, max_units: int = 2) -> str:
    units_forms = units_locale[locale]
    text_parts = []

    for unit, unit_seconds in TIME_UNITS:
        value = seconds // unit_seconds
        if value > 0:
            text_parts.append(f'{value} {num_to_words(value, word_forms=units_forms[unit])}')
            seconds -= value * unit_seconds

        if len(text_parts) >= max_units:
            break

    return (
        ' '.join(text_parts) if text_parts else f'{seconds} {num_to_words(seconds, word_forms=units_forms["seconds"])}'
    )


def num_to_words(count: int, word_forms: tuple[str, str, str]) -> str:
    if count % 10 == 1 and count % 100 != 11:  # noqa
        p = 0
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):  # noqa
        p = 1
    else:
        p = 2
    return word_forms[p]
