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


@dataclass(frozen=True, slots=True)
class OkxGridConsts(OkxBaseConsts):
    PLACE_GRID_ALGO_ORDER: ClassVar[str] = "/api/v5/tradingBot/grid/order-algo"
    AMEND_GRID_ALGO_ORDER: ClassVar[str] = "/api/v5/tradingBot/grid/amend-order-algo"
    STOP_GRID_ALGO_ORDER: ClassVar[str] = "/api/v5/tradingBot/grid/stop-order-algo"
    CLOSE_POSITION_CONTRACT_GRID: ClassVar[str] = "/api/v5/tradingBot/grid/close-position"
    CANCEL_CLOSE_POSITION_CONTRACT_GRID: ClassVar[str] = "/api/v5/tradingBot/grid/cancel-close-order"
    INSTANT_TRIGGER_GRID_ORDER: ClassVar[str] = "/api/v5/tradingBot/grid/order-instant-trigger"
    GET_GRID_ORDER_LIST: ClassVar[str] = "/api/v5/tradingBot/grid/orders-algo-pending"
    GET_GRID_ORDER_DETAILS: ClassVar[str] = "/api/v5/tradingBot/grid/orders-algo-details"
    GET_GRID_SUB_ORDERS: ClassVar[str] = "/api/v5/tradingBot/grid/sub-orders"
    SPOT_GRID_WITHDRAW_INCOME: ClassVar[str] = "/api/v5/tradingBot/grid/withdraw-income"
    COMPUTE_MARGIN_BALANCE: ClassVar[str] = "/api/v5/tradingBot/grid/compute-margin-balance"
    ADJUST_MARGIN_BALANCE: ClassVar[str] = "/api/v5/tradingBot/grid/margin-balance"
    ADD_INVESTMENT: ClassVar[str] = "/api/v5/tradingBot/grid/adjust-investment"
    GET_AI_PARAMETER_PUBLIC: ClassVar[str] = "/api/v5/tradingBot/grid/ai-param"
    COMPUTE_MIN_INVESTMENT_PUBLIC: ClassVar[str] = "/api/v5/tradingBot/grid/min-investment"
    GET_RSI_BACK_TESTING_PUBLIC: ClassVar[str] = "/api/v5/tradingBot/public/rsi-back-testing"
    GET_MAX_GRID_QUANTITY_PUBLIC: ClassVar[str] = "/api/v5/tradingBot/grid/grid-quantity"