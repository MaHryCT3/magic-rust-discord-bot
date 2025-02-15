from enum import StrEnum

from core.localization import LocaleEnum


class ActivityPeriodTypeEnum(StrEnum):
    MONTH = 'MONTH'
    WEEK = 'WEEK'
    DAYS = 'DAYS'


ACTIVITY_PERIOD_TYPE_TRANSLATE: dict[LocaleEnum, dict[ActivityPeriodTypeEnum, str]] = {
    LocaleEnum.ru: {
        ActivityPeriodTypeEnum.MONTH: 'По месяцам',
        ActivityPeriodTypeEnum.WEEK: 'По неделям',
        ActivityPeriodTypeEnum.DAYS: 'По дням',
    },
    LocaleEnum.en: {
        ActivityPeriodTypeEnum.MONTH: 'Month',
        ActivityPeriodTypeEnum.WEEK: 'Week',
        ActivityPeriodTypeEnum.DAYS: 'Days',
    },
}
