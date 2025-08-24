from abc import ABC
from typing import Any

from api_okx_v1.src.application.interfaces import (
    GetOrderDetailsDTO,
    IOkxTrade,
    IOkxExcHandler,
    ISecurity
)
from api_okx_v1.src.application.dto.trade import (
    AmendOrderDTO,
    CancelOrderDTO,
    ClosePositionsDTO,
    GetBalanceDTO,
    GetLeverageDTO,
    GetOrderListDTO,
    PlaceOrderDTO,
    SetLeverageDTO, 
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
    async def __call__(self, ccy: str) -> dict[str, Any]:
        ...


class GetPositionsInteractor(BaseTradeInteractor):
    async def __call__(self, params: GetBalanceDTO) -> dict[str, Any]:
        ...


class SetPositionModeInteractor(BaseTradeInteractor):
    async def __call__(self, posMode: str) -> dict[str, Any]:
        ...


class SetLeverageInteractor(BaseTradeInteractor):
    async def __call__(self, params: SetLeverageDTO) -> dict[str, Any]:
        ...


class GetLeverageInteractor(BaseTradeInteractor):
    async def __call__(self, params: GetLeverageDTO) -> dict[str, Any]:
        ...


class PlaceOrderInteractor(BaseTradeInteractor):
    async def __call__(self, params: PlaceOrderDTO) -> dict[str, Any]:
        ...


class AmendOrderInteractor(BaseTradeInteractor):
    async def __call__(self, params: AmendOrderDTO) -> dict[str, Any]:
        ...


class CancelOrderInteractor(BaseTradeInteractor):
    async def __call__(self, params: CancelOrderDTO) -> dict[str, Any]:
        ...


class ClosePostionsInteractor(BaseTradeInteractor):
    async def __call__(self, params: ClosePositionsDTO) -> dict[str, Any]:
        ...


class GetOrderDetailsInteractor(BaseTradeInteractor):
    async def __call__(self, params: GetOrderDetailsDTO) -> dict[str, Any]:
        ...


class GetOrderListInteracctor(BaseTradeInteractor):
    async def __call__(self, params: GetOrderListDTO) -> dict[str, Any]:
        ...
