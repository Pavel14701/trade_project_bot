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
    rsi_length: int = 14
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    scalar: float = 100.0
    drift: int = 1
    offset: int = 0
    talib: bool = True


@dataclass(slots=True, frozen=True)
class AdxConfigDM:
    length: int = 14
    lensig: int = 14
    adxr_length: int = 14
    mamode: str = "ema"
    scalar: float = 100.0
    drift: int = 1
    offset: int = 0


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
    # talib.MA_Type
    fastd_matype: int


@dataclass(slots=True, frozen=True)
class AcceletrationBandsDM:
    length: int
    drift: int
    offset: int
    mamode: str = "ema"


@dataclass(slots=True, frozen=True)
class OrderBlockDetectorDM:
    peak_prominance: float = 0.02 
    valley_prominance: float = -0.02 
    width: int = 1
    distance: int = 3 
    height:  Any | None = None
    threshold: Any | None = None
    prominence: Any | None = None
    wlen: Any | None = None
    rel_height: float = 0.5
    plateu_size: Any | None = None


@dataclass(slots=True, frozen=True)
class ScrsiConfigDM:
    domcycle: int = 20  # Основной цикл CRSI
    vibration: int = 20  # Колебания
    leveling: float = 10.0  # Уровень сглаживания

