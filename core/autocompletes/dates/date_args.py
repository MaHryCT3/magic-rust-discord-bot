import datetime

index_to_args_name_map: dict[int, str] = {
    0: 'day',
    1: 'month',
    2: 'year',
}


class PredictionDate:
    def __init__(self, raw_str):
        self._prediction_date = datetime.date.today()

        for index, item in enumerate(raw_str.split('.')):
            if not item:
                return
            self._set_attr_by_index(index, int(item))

    def get_prediction(self) -> datetime.date:
        return self._prediction_date

    def _set_attr_by_index(self, index: int, value: int) -> None:
        attr = index_to_args_name_map[index]
        self._prediction_date = self._prediction_date.replace(**{attr: value})
