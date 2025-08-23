from dataclasses import dataclass
from typing import ClassVar

@dataclass(frozen=True, slots=True)
class OkxBaseConsts:
    BASE_URL: ClassVar[str] = "https://api.okx.com"

@dataclass(frozen=True, slots=True)
class OkxMarketConsts(OkxBaseConsts):
    GET_CANDLESTICKS: ClassVar[str] = "/api/v5/market/candles"
    GET_CANDLESTICKS_HISTORY: ClassVar[str] = "/api/v5/market/history-candles"
    GET_TICKER: ClassVar[str] = "/api/v5/market/ticker"
    GET_MARK_PRICE: ClassVar[str] = "/api/v5/public/mark-price"
    GET_INSTRUMENTS: ClassVar[str] = "/api/v5/public/instruments"


