"""
Provides a concrete implementation of the OKX Trade service interface.

This module defines the `OkxTradeService` class, which extends the generic `BaseQuerySet`
and implements the `IOkxTrade` interface. It encapsulates all interactions with OKX's trading API,
including account balance retrieval, position management, leverage configuration, and order operations.

Key Responsibilities:
- Construct and send authenticated HTTP requests to OKX trading endpoints.
- Serialize request parameters using DTOs.
- Sign requests using the provided `ISignature` implementation.
- Provide high-level methods for placing, amending, canceling, and querying orders.

Dependencies:
- `BaseQuerySet`: Abstract base class for HTTP request execution and signing.
- DTOs from `api_okx_v1.src.application.dto.trade`: Define structured request payloads.
- `IOkxTrade`: Interface defining expected trading operations.
- `ISignature`: Interface for generating secure request signatures.
- `PrivateClient`: Asynchronous HTTP client for private API calls.
- `OkxTradeConsts`: Constants specific to trading endpoints.

Typical Usage:
    service = OkxTradeService(client, consts, signer)
    await service.place_order(dto, secret)
"""

from typing import Any

from api_okx_v1.src.application.dto.base import SecretDTO
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
from api_okx_v1.src.application.interfaces import (
    IOkxTrade,
    ISignature
)
from api_okx_v1.src.infrastructure._types import PrivateClient
from api_okx_v1.src.infrastructure.consts import OkxTradeConsts
from api_okx_v1.src.infrastructure.gateways.base import BaseQuerySet


class OkxTradeService(BaseQuerySet[PrivateClient, OkxTradeConsts], IOkxTrade):
    """
    Service class for interacting with OKX Trading API endpoints.

    Implements the `IOkxTrade` interface and provides methods to manage account balances,
    positions, leverage, and orders. Uses `BaseQuerySet` for shared request logic and
    integrates secure request signing via `ISignature`.
    """

    def __init__(
        self,
        private_client: PrivateClient,
        consts: OkxTradeConsts,
        security: ISignature
    ) -> None:
        self._private_client = private_client
        self._consts = consts
        self._security = security

    async def get_account_balance(
        self, 
        ccy: str,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Retrieves the account balance for a specific currency.

        Args:
            ccy (str): Currency code (e.g., "USDT", "BTC").
            secret (SecretDTO): Authentication credentials for the request.

        Returns:
            dict[str, Any]: Account balance details including available and frozen funds.
        """
        return await self.get(
            endpoint=self._consts.GET_ACCOUNT_BALANCE,
            params={"ccy": ccy},
            secret=secret
        )

    async def get_positions(
        self, 
        params: GetBalanceDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Retrieves current open positions for the authenticated account.

        Args:
            params (GetBalanceDTO): Parameters including currency and instrument type.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Position data including size, margin, and instrument info.
        """
        return await self.get(
            endpoint=self._consts.GET_POSITIONS,
            params=params,
            secret=secret
        )

    async def set_position_mode(
        self, 
        posMode: str,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Sets the position mode (e.g., net or isolated) for the account.

        Args:
            posMode (str): Desired position mode.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Confirmation of the updated position mode.
        """
        return await self.post(
            endpoint=self._consts.SET_POSITION_MODE,
            params={"posMode": posMode},
            secret=secret
        )

    async def set_leverage(
        self, 
        params: SetLeverageDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Sets leverage for a specific instrument or position.

        Args:
            params (SetLeverageDTO): Leverage configuration details.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Confirmation of leverage update.
        """
        return await self.post(
            endpoint=self._consts.SET_LEVERAGE,
            params=params,
            secret=secret
        )

    async def get_leverage(
        self, 
        params: GetLeverageDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Retrieves current leverage settings for a given instrument.

        Args:
            params (GetLeverageDTO): Instrument and account identifiers.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Current leverage configuration.
        """
        return await self.get(
            endpoint=self._consts.GET_LEVERAGE,
            params=params,
            secret=secret
        )

    async def place_order(
        self, 
        params: PlaceOrderDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Places a new order on the OKX trading platform.

        Args:
            params (PlaceOrderDTO): Order details including instrument, side, quantity, and price.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Confirmation and details of the placed order.
        """
        return await self.post(
            endpoint=self._consts.PLACE_ORDER,
            params=params,
            secret=secret
        )

    async def amend_order(
        self, 
        params: AmendOrderDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Modifies an existing order (e.g., price, quantity).

        Args:
            params (AmendOrderDTO): Amendment details including order ID and new values.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Confirmation of order amendment.
        """
        return await self.post(
            endpoint=self._consts.AMEND_ORDER,
            params=params,
            secret=secret
        )

    async def cancel_order(
        self, 
        params: CancelOrderDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Cancels an active order on the OKX platform.

        Args:
            params (CancelOrderDTO): Order ID and instrument details.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Confirmation of cancellation.
        """
        return await self.post(
            endpoint=self._consts.CANCEL_ORDER,
            params=params,
            secret=secret
        )

    async def close_positions(
        self, 
        params: ClosePositionsDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Closes open positions for the authenticated account.

        Args:
            params (ClosePositionsDTO): Position identifiers and closure details.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Confirmation of closed positions.
        """
        return await self.post(
            endpoint=self._consts.CLOSE_POSITIONS,
            params=params,
            secret=secret
        )

    async def get_order_details(
        self, 
        params: GetOrderDetailsDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific order.

        Args:
            params (GetOrderDetailsDTO): Order ID and instrument details.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: Detailed order information including status and execution history.
        """
        return await self.get(
            endpoint=self._consts.GET_ORDER_DETAILS,
            params=params,
            secret=secret
        )

    async def get_order_list(
        self, 
        params: GetOrderListDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        """
        Retrieves a list of active or historical orders for the authenticated user.

        Args:
            params (GetOrderListDTO): Filtering options such as instrument, status, and time range.
            secret (SecretDTO): Authentication credentials.

        Returns:
            dict[str, Any]: List of orders matching the query.
        """
        return await self.get(
            endpoint=self._consts.GET_ORDER_LIST,
            params=params,
            secret=secret
        )