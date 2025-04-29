from typing import Any, Protocol

from main_app.src.api.dto import (
    AmendOrderDTO,
    CancelOrerDTO,
    GetBalanceDTO,
    GetLeverageDTO,
    GetMarkPriceDTO,
    GetOrderDetailsDTO,
    GetOrderListDTO, 
    GetPriceDataDTO,
    PlaceOrderDTO,
    SetLeverageDTO,
    ClosePositionsDTO
)


class IOkxTrade(Protocol):
    # https://www.okx.com/docs-v5/en/#overview-rest-authentication-signature
    # https://www.okx.com/docs-v5/en/#overview-rest-authentication-making-requests

    async def get_account_balance(self, ccy: str) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-balance
        ...

    async def get_positions(self, params: GetBalanceDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-positions
        ...

    async def set_position_mode(self, posMode: str) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-position-mode
        ...

    async def set_leverage(self, params: SetLeverageDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-leverage
        ...

    async def get_leverage(self, params: GetLeverageDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-leverage
        ...

    async def place_order(self, params: PlaceOrderDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-place-order
        ...

    async def amend_order(self, params: AmendOrderDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-trade-post-amend-order
        ...

    async def cancel_order(self, params: CancelOrerDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-trade-post-cancel-order
        ...

    async def close_positions(self, params: ClosePositionsDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-trade-post-close-positions
        ...

    async def get_order_details(self, params: GetOrderDetailsDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-trade-get-order-details
        ...

    async def get_order_list(self, params: GetOrderListDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-trade-get-order-list
        ...



class IOkxMarketData(Protocol):
    async def get_candlesticks(self, params: GetPriceDataDTO) -> dict[str, Any]: 
        # https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-candlesticks
        ...

    async def get_candlesticks_history(self, params: GetPriceDataDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-candlesticks-history
        ...

    async def get_ticker(self, instId: str) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-ticker
        ...

    async def get_mark_price(self, params: GetMarkPriceDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#public-data-rest-api-get-mark-price
        ...

    async def get_instruments(self, instId: str) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#public-data-rest-api-get-instruments
        ...


class IOkxExcHandler(Protocol):
    async def handle_exception(self):
        # https://www.okx.com/docs-v5/en/#error-code
        ...


class IAsyncRequests(Protocol):
    pass