import pandas as pd
from typing import Iterable, Sequence, Optional, Union, Any, cast


class PriceDataFrame(pd.DataFrame):
    """
    Кастомный DataFrame с автоматической обработкой
    типов QuestDB и доступом к колонкам через атрибуты.
    """

    REQUIRED_COLUMNS: Sequence[str] = (
        "date", "open_price", "close_price", "high_price", "low_price", "volume", "turnover"
    )

    def __init__(
        self,
        data: Union[pd.DataFrame, dict[str, Any]],
        columns: Optional[Iterable[str]] = None
    ) -> None:
        super().__init__(data, columns=columns)  # type: ignore

        self._validate_columns()
        self._convert_types()
        self.set_index("date", inplace=True)  # type: ignore

    def _validate_columns(self) -> None:
        missing = [col for col in self.REQUIRED_COLUMNS if col not in self.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def _convert_types(self) -> None:
        self["date"] = pd.to_datetime(self["date"], errors="coerce")  # type: ignore
        self["open_price"] = self["open_price"].astype(float)
        self["close_price"] = self["close_price"].astype(float)
        self["high_price"] = self["high_price"].astype(float)
        self["low_price"] = self["low_price"].astype(float)
        self["volume"] = self["volume"].astype(int)
        self["turnover"] = self["turnover"].astype(float)

    @property
    def date(self) -> pd.DatetimeIndex:
        if isinstance(self.index, pd.DatetimeIndex): # type: ignore
            return self.index
        raise TypeError("Expected DatetimeIndex as index")

    @property
    def open_price(self) -> pd.Series[float]:
        return cast(pd.Series[float], self["open_price"])

    @property
    def close_prices(self) -> pd.Series[float]:
        return cast(pd.Series[float], self["close_price"])

    @property
    def high_prices(self) -> pd.Series[float]:
        return cast(pd.Series[float], self["high_price"])

    @property
    def low_prices(self) -> pd.Series[float]:
        return cast(pd.Series[float], self["low_price"])

    @property
    def volumes(self) -> pd.Series[int]:
        return cast(pd.Series[int], self["volume"])

    @property
    def turnover(self) -> pd.Series[float]:
        return cast(pd.Series[float], self["turnover"])
