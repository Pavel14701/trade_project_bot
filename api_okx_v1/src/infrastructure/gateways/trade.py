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
    ISecurity
)
from api_okx_v1.src.infrastructure._types import PrivateClient
from api_okx_v1.src.infrastructure.consts import OkxTradeConsts
from api_okx_v1.src.infrastructure.gateways.base import BaseQuerySet


class OkxMarketService(
    BaseQuerySet[PrivateClient, OkxTradeConsts], 
    IOkxTrade
):
    def __init__(
        self,
        private_client: PrivateClient,
        consts: OkxTradeConsts,
        security: ISecurity
    ) -> None:
        self._private_client = private_client
        self._consts = consts
        self._security = security

    async def get_account_balance(
        self, 
        ccy: str,
        secret: SecretDTO
    ) -> dict[str, Any]:
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
        return await self.get(
            endpoint=self._consts.GET_ORDER_LIST,
            params=params,
            secret=secret
        )