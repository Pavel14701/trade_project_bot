"""
Provides a concrete implementation of the OKX Grid Trading service interface.

This module defines the `OkxGridService` class, which extends the abstract `BaseQuerySet` and implements
the `IOkxGridTrade` interface. It encapsulates all interactions with the OKX Grid Trading API, including
placing, amending, stopping, and querying grid orders, as well as managing margin and investment operations.

Key Responsibilities:
- Construct and send authenticated HTTP requests to OKX grid trading endpoints.
- Serialize and validate request payloads using DTOs.
- Sign requests using the provided `ISignature` implementation.
- Handle both private and public grid trading operations.

Dependencies:
- `BaseQuerySet`: Provides shared request logic such as signing, parameter preparation, and HTTP execution.
- `SecretDTO`: Contains user-specific API credentials.
- DTOs from `api_okx_v1.src.application.dto.grid`: Define structured request payloads for each API operation.
- `IOkxGridTrade`: Interface defining the expected grid trading operations.
- `ISignature`: Interface for generating secure request signatures.
- `PrivateClient`: Asynchronous HTTP client for private API calls.
- `OkxGridConsts`: Constants specific to the grid trading domain (e.g., base URLs, endpoints).

Typical Usage:
    service = OkxGridService(client, consts, signer)
    await service.place_grid_order(dto, secret)

This service is intended to be used within a larger application or controller layer that handles
message routing, user input, and orchestration of trading workflows.
"""


from typing import Any

from api_okx_v1.src.application.dto.base import SecretDTO
from api_okx_v1.src.application.dto.grid import (
    PlaceGridOrderDTO,
    AmendGridOrderDTO,
    StopGridOrderDTO,
    CloseContractGridDTO,
    CancelCloseContractGridDTO,
    GetGridOrderListDTO,
    GetGridOrderDetailsDTO,
    GetGridSubOrdersDTO,
    ComputeMarginBalanceDTO,
    AdjustMarginBalanceDTO,
    AddIvestmentDTO,
    AiParamsPublicDTO,
    ComputeMinInvestmentPublicDTO,
    RsiBacktestingPublicDTO,
    MaxGridQuantityPublicDTO
) 
from api_okx_v1.src.application.interfaces import (
    IOkxGridTrade,
    ISignature
)
from api_okx_v1.src.infrastructure._types import PrivateClient
from api_okx_v1.src.infrastructure.consts import OkxGridConsts
from api_okx_v1.src.infrastructure.gateways.base import BaseQuerySet


class OkxGridService(BaseQuerySet[PrivateClient, OkxGridConsts], IOkxGridTrade):
    """
    Service class for interacting with OKX Grid Trading API endpoints.
    Provides methods to place, amend, stop, and query grid trading orders,
    as well as manage margin and investment operations.
    """
    def __init__(
        self,
        private_client: PrivateClient,
        consts: OkxGridConsts,
        security: ISignature
    ) -> None:
        self._private_client = private_client
        self._consts = consts
        self._security = security

    async def place_grid_algo_order(
        self, 
        params: PlaceGridOrderDTO, 
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Place a new grid algorithmic trading order.

        Args:
            params (PlaceGridOrderDTO): Parameters for placing the grid order.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.post(
            endpoint=self._consts.PLACE_GRID_ALGO_ORDER,
            params=params,
            secret=secret
        )

    async def amend_grid_algo_order(
        self, 
        params: AmendGridOrderDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Amend an existing grid algorithmic trading order.

        Args:
            params (AmendGridOrderDTO): Parameters for amending the grid order.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.post(
            endpoint=self._consts.AMEND_GRID_ALGO_ORDER,
            params=params,
            secret=secret
        )

    async def stop_grid_algo_order(
        self, 
        params: StopGridOrderDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Stop an active grid algorithmic trading order.

        Args:
            params (StopGridOrderDTO): Parameters for stopping the grid order.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.post(
            endpoint=self._consts.STOP_GRID_ALGO_ORDER,
            params=params,
            secret=secret
        )

    async def close_position_for_contract_grid(
        self, 
        params: CloseContractGridDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Close a position for a contract-based grid order.

        Args:
            params (CloseContractGridDTO): Parameters for closing the position.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.post(
            endpoint=self._consts.CLOSE_POSITION_CONTRACT_GRID,
            params=params,
            secret=secret
        )

    async def cancel_close_position_for_contract_grid(
        self, 
        params: CancelCloseContractGridDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Cancel a previously requested position close for a contract-based grid order.

        Args:
            params (CancelCloseContractGridDTO): Parameters for canceling the close request.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.post(
            endpoint=self._consts.CANCEL_CLOSE_POSITION_CONTRACT_GRID,
            params=params,
            secret=secret
        )

    async def instant_trigger_grid_order(
        self, 
        algoId: str,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Instantly trigger a grid order by its algorithm ID.

        Args:
            algoId (str): Identifier of the grid algorithm.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.post(
            endpoint=self._consts.INSTANT_TRIGGER_GRID_ORDER,
            params={'algoId': algoId},
            secret=secret
        )

    async def get_grid_order_list(
        self, 
        params: GetGridOrderListDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Retrieve a list of grid trading orders.

        Args:
            params (GetGridOrderListDTO): Query parameters for retrieving the order list.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.get(
            endpoint=self._consts.GET_GRID_ORDER_LIST,
            params=params,
            secret=secret
        )

    async def get_grid_order_details(
        self, 
        params: GetGridOrderDetailsDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Retrieve detailed information about a specific grid order.

        Args:
            params (GetGridOrderDetailsDTO): Parameters identifying the grid order.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.get(
            endpoint=self._consts.GET_GRID_ORDER_DETAILS,
            params=params,
            secret=secret
        )

    async def get_grid_sub_orders(
        self, 
        params: GetGridSubOrdersDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Retrieve sub-orders associated with a grid order.

        Args:
            params (GetGridSubOrdersDTO): Parameters identifying the grid order.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.get(
            endpoint=self._consts.GET_GRID_ORDER_DETAILS,
            params=params,
            secret=secret
        )

    async def spot_grid_withdraw_income(
        self, 
        algoId: str,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Withdraw income generated from a spot grid order.

        Args:
            algoId (str): Identifier of the grid algorithm.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.post(
            endpoint=self._consts.SPOT_GRID_WITHDRAW_INCOME,
            params={'algoId': algoId},
            secret=secret
        )

    async def compute_margin_balance(
        self, 
        params: ComputeMarginBalanceDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Compute the margin balance for a grid order.

        Args:
            params (ComputeMarginBalanceDTO): Parameters for margin computation.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.post(
            endpoint=self._consts.COMPUTE_MARGIN_BALANCE,
            params=params,
            secret=secret
        )

    async def adjust_margin_balance(
        self, 
        params: AdjustMarginBalanceDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Adjust the margin balance for a grid order.

        Args:
            params (AdjustMarginBalanceDTO): Parameters for margin adjustment.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.post(
            endpoint=self._consts.ADJUST_MARGIN_BALANCE,
            params=params,
            secret=secret
        )

    async def add_investment(
        self, 
        params: AddIvestmentDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Add investment to an existing grid order.

        Args:
            params (AddIvestmentDTO): Parameters for adding investment.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.post(
            endpoint=self._consts.ADD_INVESTMENT,
            params=params,
            secret=secret
        )

    async def get_ai_parameter_public(
        self, 
        params: AiParamsPublicDTO
    ) -> dict[str, Any]:
        """
        Retrieve public AI parameters for grid trading.

        Args:
            params (AiParamsPublicDTO): Parameters for the AI query.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.get(
            endpoint=self._consts.GET_AI_PARAMETER_PUBLIC,
            params=params
        )

    async def compute_min_investment_public(
        self, 
        params: ComputeMinInvestmentPublicDTO
    ) -> dict[str, Any]:
        """
        Compute the minimum investment required for a public grid strategy.

        Args:
            params (ComputeMinInvestmentPublicDTO): Parameters for investment computation.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.post(
            endpoint=self._consts.COMPUTE_MIN_INVESTMENT_PUBLIC,
            params=params
        )

    async def get_rsi_back_testing_public(
        self, 
        params: RsiBacktestingPublicDTO
    ) -> dict[str, Any]:
        """
        Retrieve RSI backtesting results for public grid strategies.

        Args:
            params (RsiBacktestingPublicDTO): Parameters for backtesting.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.get(
            endpoint=self._consts.GET_RSI_BACK_TESTING_PUBLIC,
            params=params
        )

    async def get_max_grid_quantity_public(
        self, 
        params: MaxGridQuantityPublicDTO
    ) -> dict[str, Any]:
        """
        Retrieve the maximum grid quantity allowed for public strategies.

        Args:
            params (MaxGridQuantityPublicDTO): Parameters for the query.

        Returns:
            dict[str, Any]: Response from the API.
        """
        return await self.get(
            endpoint=self._consts.GET_MAX_GRID_QUANTITY_PUBLIC,
            params=params
        )