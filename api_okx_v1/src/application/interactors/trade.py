from abc import ABC
from typing import Any

from application.dto.base import SecretDTO
from application.dto.trade import (
    AmendOrderDTO,
    CancelOrderDTO,
    ClosePositionsDTO,
    GetBalanceDTO,
    GetLeverageDTO,
    GetOrderListDTO,
    PlaceOrderDTO,
    SetLeverageDTO,
)
from application.interfaces import (
    GetOrderDetailsDTO,
    IOkxExcHandler,
    IOkxTrade,
    ISecurity,
)


class BaseTradeInteractor(ABC):
    def __init__(
        self,
        gateway: IOkxTrade,
        security: ISecurity,
        exc_handler: IOkxExcHandler
    ) -> None:
        self._gateway = gateway
        self._security = security
        self._exc_handler = exc_handler


class GetAccountBalanceInteractor(BaseTradeInteractor):
    async def __call__(
        self, 
        ccy: str, 
        secret: SecretDTO
    ) -> dict[str, Any]:
        return await self._gateway.get_account_balance(ccy, secret)


class GetPositionsInteractor(BaseTradeInteractor):
    async def __call__(
        self, 
        params: GetBalanceDTO, 
        secret: SecretDTO
    ) -> dict[str, Any]:
        return await self._gateway.get_positions(params=params, secret=secret)


class SetPositionModeInteractor(BaseTradeInteractor):
    async def __call__(
        self, 
        posMode: str,
        secret: SecretDTO
    ) -> dict[str, Any]:
        return await self._gateway.set_position_mode(posMode=posMode, secret=secret)


class SetLeverageInteractor(BaseTradeInteractor):
    async def __call__(
        self, 
        params: SetLeverageDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        return await self._gateway.set_leverage(params=params, secret=secret)


class GetLeverageInteractor(BaseTradeInteractor):
    async def __call__(
        self, 
        params: GetLeverageDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        return await self._gateway.get_leverage(params=params, secret=secret)


class PlaceOrderInteractor(BaseTradeInteractor):
    async def __call__(
        self, 
        params: PlaceOrderDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        return await self._gateway.place_order(params, secret)


class AmendOrderInteractor(BaseTradeInteractor):
    async def __call__(
        self, 
        params: AmendOrderDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        return await self._gateway.amend_order(params, secret)


class CancelOrderInteractor(BaseTradeInteractor):
    async def __call__(
        self, 
        params: CancelOrderDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        return await self._gateway.cancel_order(params, secret)


class ClosePostionsInteractor(BaseTradeInteractor):
    async def __call__(
        self, 
        params: ClosePositionsDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        return await self._gateway.close_positions(params, secret)


class GetOrderDetailsInteractor(BaseTradeInteractor):
    async def __call__(
        self, 
        params: GetOrderDetailsDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        return await self._gateway.get_order_details(params, secret)


class GetOrderListInteractor(BaseTradeInteractor):
    async def __call__(
        self, 
        params: GetOrderListDTO,
        secret: SecretDTO
    ) -> dict[str, Any]:
        return await self._gateway.get_order_list(params, secret)