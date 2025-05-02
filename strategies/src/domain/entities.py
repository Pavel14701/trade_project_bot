from dataclasses import dataclass


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
