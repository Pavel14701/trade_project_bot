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


@dataclass(frozen=True, slots=True)
class OkxTradeConsts(OkxBaseConsts):
    GET_ACCOUNT_BALANCE: ClassVar[str] = "/api/v5/account/balance"
    GET_POSITIONS: ClassVar[str] = "/api/v5/account/positions"
    SET_POSITION_MODE: ClassVar[str] = "/api/v5/account/set-position-mode"
    SET_LEVERAGE: ClassVar[str] = "/api/v5/account/set-leverage"
    GET_LEVERAGE: ClassVar[str] = "/api/v5/account/leverage-info"
    PLACE_ORDER: ClassVar[str] = "/api/v5/trade/order"
    AMEND_ORDER: ClassVar[str] = "/api/v5/trade/amend-order"
    CANCEL_ORDER: ClassVar[str] = "/api/v5/trade/cancel-order"
    CLOSE_POSITIONS: ClassVar[str] = "/api/v5/trade/close-position"
    GET_ORDER_DETAILS: ClassVar[str] = "/api/v5/trade/order"
    GET_ORDER_LIST: ClassVar[str] = "/api/v5/trade/orders-pending"