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


class OkxGridService(
    BaseQuerySet[PrivateClient, OkxGridConsts], 
    IOkxGridTrade
):
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
        return await self.post(
            endpoint=self._consts.ADD_INVESTMENT,
            params=params,
            secret=secret
        )

    async def get_ai_parameter_public(
        self, 
        params: AiParamsPublicDTO
    ) -> dict[str, Any]:
        return await self.get(
            endpoint=self._consts.GET_AI_PARAMETER_PUBLIC,
            params=params
        )

    async def compute_min_investment_public(
        self, 
        params: ComputeMinInvestmentPublicDTO
    ) -> dict[str, Any]:
        return await self.post(
            endpoint=self._consts.COMPUTE_MIN_INVESTMENT_PUBLIC,
            params=params
        )

    async def get_rsi_back_testing_public(
        self, 
        params: RsiBacktestingPublicDTO
    ) -> dict[str, Any]:
        return await self.get(
            endpoint=self._consts.COMPUTE_MIN_INVESTMENT_PUBLIC,
            params=params
        )

    async def get_max_grid_quantity_public(
        self, 
        params: MaxGridQuantityPublicDTO
    ) -> dict[str, Any]:
        return await self.get(
            endpoint=self._consts.COMPUTE_MIN_INVESTMENT_PUBLIC,
            params=params
        )