from typing import Any, Protocol

from api_okx_v1.src.application.dto.base import SecretDTO
from api_okx_v1.src.application.dto.grid import (
    AddIvestmentDTO,
    AdjustMarginBalanceDTO,
    AiParamsPublicDTO,
    AmendGridOrderDTO,
    CancelCloseContractGridDTO,
    CloseContractGridDTO,
    ComputeMarginBalanceDTO,
    ComputeMinInvestmentPublicDTO,
    GetGridOrderDetailsDTO,
    GetGridOrderListDTO,
    GetGridSubOrersDTO,
    MaxGridQuantityPublicDTO,
    PlaceGridOrderDTO,
    RsiBacktestingPublicDTO,
    StopGridOrderDTO,
)
from api_okx_v1.src.application.dto.market import (
    GetMarketPriceDTO,
    GetPriceDataDTO,
    GetInstrumentsDTO,
)
from api_okx_v1.src.application.dto.trade import (
    AmendOrderDTO,
    CancelOrderDTO,
    ClosePositionsDTO,
    GetBalanceDTO,
    GetLeverageDTO,
    GetOrderDetailsDTO,
    GetOrderListDTO,
    PlaceOrderDTO,
    SetLeverageDTO,
)
from api_okx_v1.src.domain.entities import (
    SignatureDM
)


class IOkxTrade(Protocol):
    # https://www.okx.com/docs-v5/en/#overview-rest-authentication-signature
    # https://www.okx.com/docs-v5/en/#overview-rest-authentication-making-requests

    async def get_account_balance(
        self, 
        ccy: str
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-balance
        raise NotImplementedError()

    async def get_positions(
        self, 
        params: GetBalanceDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-positions
        raise NotImplementedError()

    async def set_position_mode(
        self, 
        posMode: str,
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-position-mode
        raise NotImplementedError()

    async def set_leverage(
        self, 
        params: SetLeverageDTO,
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-leverage
        raise NotImplementedError()

    async def get_leverage(
        self, 
        params: GetLeverageDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-leverage
        raise NotImplementedError()

    async def place_order(
        self, 
        params: PlaceOrderDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-place-order
        raise NotImplementedError()

    async def amend_order(
        self, 
        params: AmendOrderDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-trade-post-amend-order
        raise NotImplementedError()

    async def cancel_order(
        self, 
        params: CancelOrderDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-trade-post-cancel-order
        raise NotImplementedError()

    async def close_positions(
        self, 
        params: ClosePositionsDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-trade-post-close-positions
        raise NotImplementedError()

    async def get_order_details(
        self, 
        params: GetOrderDetailsDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-trade-get-order-details
        raise NotImplementedError()

    async def get_order_list(
        self, 
        params: GetOrderListDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-trade-get-order-list
        raise NotImplementedError()


class IOkcGridTrade(Protocol):
    async def place_grid_algo_order(
        self, 
        params: PlaceGridOrderDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-place-grid-algo-order
        raise NotImplementedError()

    async def amend_grid_algo_order(
        self, 
        params: AmendGridOrderDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-amend-grid-algo-order
        raise NotImplementedError()

    async def stop_grid_algo_order(
        self, 
        params: StopGridOrderDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-stop-grid-algo-order
        raise NotImplementedError()

    async def close_position_for_contract_grid(
        self, 
        params: CloseContractGridDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-close-position-for-contract-grid
        raise NotImplementedError()

    async def cancel_close_position_for_contract_grid(
        self, 
        params: CancelCloseContractGridDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-cancel-close-position-order-for-contract-grid
        raise NotImplementedError()

    async def instant_trigger_grid_order(
        self, 
        algoId: str
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-instant-trigger-grid-algo-order
        raise NotImplementedError()

    async def get_grid_order_list(
        self, 
        params: GetGridOrderListDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-get-grid-algo-order-list
        raise NotImplementedError()

    async def get_grid_order_details(
        self, 
        params: GetGridOrderDetailsDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-get-grid-algo-order-details
        raise NotImplementedError()

    async def get_grid_sub_orders(
        self, 
        params: GetGridSubOrersDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-get-grid-algo-sub-orders
        raise NotImplementedError()

    async def spot_grid_withdraw_income(
        self, 
        algoId: str
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-spot-grid-withdraw-income
        raise NotImplementedError()

    async def compute_margin_balance(
        self, 
        params: ComputeMarginBalanceDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-compute-margin-balance
        raise NotImplementedError()

    async def adjust_margin_balance(
        self, 
        params: AdjustMarginBalanceDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-adjust-margin-balance
        raise NotImplementedError()

    async def add_investment(
        self, 
        params: AddIvestmentDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-add-investment
        raise NotImplementedError()

    async def get_ai_parameter_public(
        self, 
        params: AiParamsPublicDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-get-grid-ai-parameter-public
        raise NotImplementedError()

    async def compute_min_investment_public(
        self, 
        params: ComputeMinInvestmentPublicDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-post-compute-min-investment-public
        raise NotImplementedError()

    async def get_rsi_back_testing_public(
        self, 
        params: RsiBacktestingPublicDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-get-rsi-back-testing-public
        raise NotImplementedError()

    async def get_max_grid_quantity_public(
        self, 
        params: MaxGridQuantityPublicDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/?shell#order-book-trading-grid-trading-get-max-grid-quantity-public
        raise NotImplementedError()


class IOkxMarketData(Protocol):
    async def get_candlesticks(
        self, 
        params: GetPriceDataDTO
    ) -> dict[str, Any]: 
        # https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-candlesticks
        raise NotImplementedError()

    async def get_candlesticks_history(
        self, 
        params: GetPriceDataDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-candlesticks-history
        raise NotImplementedError()

    async def get_ticker(
        self, 
        instId: str
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-ticker
        raise NotImplementedError()

    async def get_mark_price(
        self, 
        params: GetMarketPriceDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#public-data-rest-api-get-mark-price
        raise NotImplementedError()

    async def get_instruments(
        self, 
        params: GetInstrumentsDTO
    ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#public-data-rest-api-get-instruments
        raise NotImplementedError()


class IOkxExcHandler(Protocol):
    async def __call__(self) -> Any:
        # url link for exception handler
        # (works only for Chrome, probably, but not for sure)
        # https://www.okx.com/docs-v5/en/#error-code-rest-api-public#:~:text=50005
        raise NotImplementedError()


class ISecurity(Protocol):
    async def encrypt(
        self, 
        model: SecretDTO
    ) -> SecretDTO:
        raise NotImplementedError()

    async def decrypt(
        self, 
        model: SecretDTO
    ) -> SecretDTO:
        raise NotImplementedError()


class ISignature(Protocol):
    async def get_signature(
        self, 
        params: SignatureDM
    ) -> dict[str, str]:
        raise NotImplementedError()


class IAsyncRequests(Protocol):
    pass