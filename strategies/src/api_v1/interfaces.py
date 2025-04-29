from typing import Any, Protocol

from strategies.src.api_v1.dto.grid import (
    AddIvestmentDTO,
    AmendGridOrderDTO,
    CancelCloseContractGridDTO,
    CloseContractGridDTO,
    ComputeMinInvestmentPublicDTO,
    MaxGridQuantityPublicDTO,
    PlaceGridOrderDTO,
    RsiBacktestingPublicDTO,
    StopGridOrderDTO,
    GetGridOrderListDTO,
    GetGridOrderDetailsDTO,
    GetGridSubOrersDTO,
    ComputeMarginBalanceDTO,
    AdjustMarginBalanceDTO,
    AiParamsPublicDTO
)
from strategies.src.api_v1.dto.market import (
    GetMarkPriceDTO,
    GetPriceDataDTO,
)
from strategies.src.api_v1.dto.trade import (
    AmendOrderDTO,
    CancelOrerDTO,
    ClosePositionsDTO,
    GetBalanceDTO,
    GetLeverageDTO,
    GetOrderDetailsDTO,
    GetOrderListDTO,
    PlaceOrderDTO,
    SetLeverageDTO,
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


class IOkcGridTrade(Protocol):
    async def place_grid_algo_order(self, params: PlaceGridOrderDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-place-grid-algo-order
        ...

    async def amend_grid_algo_order(self, params: AmendGridOrderDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-amend-grid-algo-order
        ...

    async def stop_grid_algo_order(self, params: StopGridOrderDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-stop-grid-algo-order
        ...

    async def close_position_for_contract_grid(
        self, 
        params: CloseContractGridDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-close-position-for-contract-grid
        ...

    async def cancel_close_position_for_contract_grid(
        self, 
        params: CancelCloseContractGridDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-cancel-close-position-order-for-contract-grid
        ...

    async def instant_trigger_grid_order(self, algoId: str) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-instant-trigger-grid-algo-order
        ...

    async def get_grid_order_list(self, params: GetGridOrderListDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-get-grid-algo-order-list
        ...

    async def get_grid_order_details(self, params: GetGridOrderDetailsDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-get-grid-algo-order-details
        ...

    async def get_grid_sub_orders(self, params: GetGridSubOrersDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-get-grid-algo-sub-orders
        ...

    async def spot_grid_withdraw_income(self, algoId: str) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-spot-grid-withdraw-income
        ...

    async def compute_margin_balance(self, params: ComputeMarginBalanceDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-compute-margin-balance
        ...

    async def adjust_margin_balance(self, params: AdjustMarginBalanceDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-adjust-margin-balance
        ...

    async def add_investment(self, params: AddIvestmentDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-add-investment
        ...

    async def get_ai_parameter_public(self, params: AiParamsPublicDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-get-grid-ai-parameter-public
        ...

    async def compute_min_investment_public(self, params: ComputeMinInvestmentPublicDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-compute-min-investment-public
        ...

    async def get_rsi_back_testing_public(self, params: RsiBacktestingPublicDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-get-rsi-back-testing-public
        ...

    async def get_max_grid_quantity_public(self, params: MaxGridQuantityPublicDTO) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-get-max-grid-quantity-public
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