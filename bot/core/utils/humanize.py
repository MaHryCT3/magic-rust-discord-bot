from typing import Final, TypeAlias, TypedDict

from bot.core.localization import LocaleEnum

ONE_HOUR_SECONDS: Final[int] = 3600


WordForms: TypeAlias = tuple[str, str, str]


class TimeUnit(TypedDict):
    seconds: WordForms
    hours: WordForms
    minutes: WordForms


units_locale: dict[LocaleEnum, TimeUnit] = {
    LocaleEnum.en: TimeUnit(
        seconds=('second', 'second', 'seconds'),
        hours=('hour', 'hour', 'hours'),
        minutes=('minute', 'minute', 'minutes'),
    ),
    LocaleEnum.ru: TimeUnit(
        seconds=('секунда', 'секунды', 'секунд'),
        hours=('час', 'часа', 'часов'),
        minutes=('минута', 'минуты', 'минут'),
    ),
}


def human_time(seconds: int, locale: LocaleEnum) -> str:
    text = ''

    units_forms = units_locale[locale]

    hours = int(seconds // ONE_HOUR_SECONDS)
    if hours > 0:
        hours_word = num_to_words(hours, word_forms=units_forms['hours'])
        text += f'{hours} {hours_word}'

    minutes = int((seconds - hours * ONE_HOUR_SECONDS) // 60)
    if minutes > 0:
        minutes_word = num_to_words(minutes, word_forms=units_forms['minutes'])
        text += f' {minutes} {minutes_word}'

    if text == '':
        seconds_text = num_to_words(seconds, word_forms=units_forms['seconds'])
        return f'{int(seconds)} {seconds_text}'

    return text


def num_to_words(count: int, word_forms: tuple[str, str, str]) -> str:
    if count % 10 == 1 and count % 100 != 11:  # noqa
        p = 0
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):  # noqa
        p = 1
    else:
        p = 2
    return word_forms[p]
