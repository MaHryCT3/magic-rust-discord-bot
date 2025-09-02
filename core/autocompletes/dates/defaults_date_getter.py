import datetime


def get_default_prediction_date_getter(
    time_moving: datetime.timedelta | None = None,
):
    def default_prediction_date_getter() -> datetime.date:
        return datetime.date.today() + time_moving

    return default_prediction_date_getter
