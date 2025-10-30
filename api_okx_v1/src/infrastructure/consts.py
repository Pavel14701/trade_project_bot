"""
Defines constant values for interacting with various OKX API domains.

This module provides structured dataclasses that group endpoint paths for:
- Market data operations
- Trading operations
- Grid trading operations

Each class inherits from `OkxBaseConsts`, which defines the base URL for all OKX API requests.
These constants are used throughout the application to construct full request URLs in service layers.
"""


from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class OkxBaseConsts:
    """
    Base class for OKX API constants.

    Defines the shared base URL used across all OKX API domains.

    Attributes:
        BASE_URL (str): The root URL for OKX API requests.
    """
    BASE_URL: ClassVar[str] = "https://api.okx.com"


@dataclass(frozen=True, slots=True)
class OkxMarketConsts(OkxBaseConsts):
    """
    Contains endpoint paths for OKX Market Data API.

    Attributes:
        GET_CANDLESTICKS (str): Endpoint for current candlestick data.
        GET_CANDLESTICKS_HISTORY (str): Endpoint for historical candlestick data.
        GET_TICKER (str): Endpoint for real-time ticker information.
        GET_MARK_PRICE (str): Endpoint for mark price used in margin calculations.
        GET_INSTRUMENTS (str): Endpoint for listing available trading instruments.
    """
    GET_CANDLESTICKS: ClassVar[str] = "/api/v5/market/candles"
    GET_CANDLESTICKS_HISTORY: ClassVar[str] = "/api/v5/market/history-candles"
    GET_TICKER: ClassVar[str] = "/api/v5/market/ticker"
    GET_MARK_PRICE: ClassVar[str] = "/api/v5/public/mark-price"
    GET_INSTRUMENTS: ClassVar[str] = "/api/v5/public/instruments"


@dataclass(frozen=True, slots=True)
class OkxTradeConsts(OkxBaseConsts):
    """
    Contains endpoint paths for OKX Trading API operations.

    Attributes:
        GET_ACCOUNT_BALANCE (str): Endpoint for retrieving account balances.
        GET_POSITIONS (str): Endpoint for fetching open positions.
        SET_POSITION_MODE (str): Endpoint for setting position mode (net/isolated).
        SET_LEVERAGE (str): Endpoint for configuring leverage.
        GET_LEVERAGE (str): Endpoint for retrieving leverage settings.
        PLACE_ORDER (str): Endpoint for placing a new order.
        AMEND_ORDER (str): Endpoint for modifying an existing order.
        CANCEL_ORDER (str): Endpoint for canceling an active order.
        CLOSE_POSITIONS (str): Endpoint for closing open positions.
        GET_ORDER_DETAILS (str): Endpoint for retrieving order details.
        GET_ORDER_LIST (str): Endpoint for listing active or pending orders.
    """
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
    """
    Contains endpoint paths for OKX Grid Trading API operations.

    Attributes:
        PLACE_GRID_ALGO_ORDER (str): Endpoint for placing a grid algorithm order.
        AMEND_GRID_ALGO_ORDER (str): Endpoint for modifying a grid algorithm order.
        STOP_GRID_ALGO_ORDER (str): Endpoint for stopping a grid algorithm order.
        CLOSE_POSITION_CONTRACT_GRID (str): Endpoint for closing grid contract positions.
        CANCEL_CLOSE_POSITION_CONTRACT_GRID (str): Endpoint for canceling grid contract closure.
        INSTANT_TRIGGER_GRID_ORDER (str): Endpoint for triggering grid orders instantly.
        GET_GRID_ORDER_LIST (str): Endpoint for listing pending grid orders.
        GET_GRID_ORDER_DETAILS (str): Endpoint for retrieving grid order details.
        GET_GRID_SUB_ORDERS (str): Endpoint for fetching sub-orders of a grid strategy.
        SPOT_GRID_WITHDRAW_INCOME (str): Endpoint for withdrawing grid trading income.
        COMPUTE_MARGIN_BALANCE (str): Endpoint for computing margin balance for grid strategies.
        ADJUST_MARGIN_BALANCE (str): Endpoint for adjusting margin balance.
        ADD_INVESTMENT (str): Endpoint for adding investment to a grid strategy.
        GET_AI_PARAMETER_PUBLIC (str): Endpoint for retrieving AI-generated grid parameters.
        COMPUTE_MIN_INVESTMENT_PUBLIC (str): Endpoint for computing minimum investment requirements.
        GET_RSI_BACK_TESTING_PUBLIC (str): Endpoint for retrieving RSI backtesting results.
        GET_MAX_GRID_QUANTITY_PUBLIC (str): Endpoint for computing maximum grid quantity.
    """
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