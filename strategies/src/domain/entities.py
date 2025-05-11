from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class CreateTableDM:
    instId: str
    bar: str
    partition: str | None = None


@dataclass(slots=True, frozen=True)
class GetLastRecordsDM:
    instId: str
    bar: str
    n: int


@dataclass(slots=True, frozen=True)
class GetRangeRecordsDM:
    instId: str
    bar: str
    start_date: str
    end_date: str


@dataclass(slots=True, frozen=True)
class Data:
    date: str
    open_price: float
    close_price: float
    high_price: float
    low_price: float
    volume: int
    turnover: float


@dataclass(slots=True, frozen=True)
class InsertRecordDM(Data):
    instId: str
    bar: str


@dataclass(slots=True, frozen=True)
class InsertManyRecordsDM:
    instId: str
    bar: str
    data: list[Data]


@dataclass(slots=True, frozen=True)
class RsiCloudsConfigDM:
    rsi_length: int | None = None
    macd_fast: int | None = None
    macd_slow: int | None = None
    macd_signal: int | None = None
    scalar: float | None = None
    drift: int | None = None
    offset: int | None = None
    talib: bool = True


@dataclass(slots=True, frozen=True)
class AdxConfigDM:
    length: int | None = None
    lensig: int | None = None
    mamode: str | None = None 
    scalar: float | int | None = None 
    drift: int | None = None
    offset: int | None = None


@dataclass(slots=True, frozen=True)
class AvslConfigDM:
    length_fast: int
    length_slow: int
    stand_div: float


@dataclass(slots=True, frozen=True)
class StochRsiConfigDM:
    timeperiod: int
    fastk_period: int 
    fastd_period: int
    #talib.MA_Type
    fastd_matype: int


@dataclass(slots=True, frozen=True)
class AcceletrationBandsDM:
    length: int
    drift: int
    offset: int
    mamode: str | None = None


@dataclass(slots=True, frozen=True)
class OrderBlockDetectorDM:
    peak_prominance: float = 0.02 
    valley_prominance: float = -0.02 
    width: int = 1
    distance: int = 3 
    height:  Any | None = None
    threshould: Any | None = None
    distance: Any | None = None
    prominence: Any | None = None
    width: Any | None = None
    wlen: Any | None = None
    rel_height: float = 0.5
    plateu_size: Any | None  = None


@dataclass(slots=True, frozen=True)
class ScrsiConfigDM:
    domcycle: int = 20  # Основной цикл CRSI
    vibration: int = 20  # Колебания
    leveling: float =  10.0  # Уровень сглаживания

