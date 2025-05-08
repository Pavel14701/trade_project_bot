from typing import Union
import pandas as pd

class PriceDataFrame(pd.DataFrame):
    """
    Кастомный DataFrame с автоматической обработкой
    типов QuestDB и доступом к колонкам через атрибуты.
    """
    def __init__(self, data, columns):
        super().__init__(data, columns=columns)
        self._convert_types()
        self.set_index("date", inplace=True)

    def _convert_types(self):
        """
        Приводим типы данных в соответствие
        с таблицей QuestDB.
        """
        self["date"] = pd.to_datetime(self["date"])
        self["open_price"] = self["open_price"].astype(float)
        self["close_price"] = self["close_price"].astype(float)
        self["high_price"] = self["high_price"].astype(float)
        self["low_price"] = self["low_price"].astype(float)
        self["volume"] = self["volume"].astype(int)
        self["turnover"] = self["turnover"].astype(float)

    @property
    def date(self) -> pd.Index:
        return self.index

    @property
    def open_price(self) -> pd.Series:
        return self["open_price"]

    @property
    def close_prices(self) -> pd.Series:
        return self["close_price"]

    @property
    def high_price(self) -> pd.Series:
        return self["high_price"]

    @property
    def low_prices(self) -> pd.Series:
        return self["low_price"]

    @property
    def volumes(self) -> pd.Series:
        return self["volume"]

    @property
    def turnover(self) -> pd.Series:
        return self["turnover"]
