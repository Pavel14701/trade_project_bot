from pandas import DataFrame, to_datetime

class PriceDataFrame(DataFrame):
    """Кастомный DataFrame с автоматической обработкой типов QuestDB."""
    def __init__(self, data, columns):
        super().__init__(data, columns=columns)
        self._convert_types()

    def _convert_types(self):
        self["date"] = to_datetime(self["date"])
        self["open_price"] = self["open_price"].astype(float)
        self["close_price"] = self["close_price"].astype(float)
        self["high_price"] = self["high_price"].astype(float)
        self["low_price"] = self["low_price"].astype(float)
        self["volume"] = self["volume"].astype(int)
        self["turnover"] = self["turnover"].astype(float)
