from typing import Any
from api_okx_v1.src.application.dto.market import (
    GetInstrumentsDTO,
    GetPriceDataDTO,
    GetMarketPriceDTO
)
from api_okx_v1.src.application.interfaces import IOkxMarketData
from api_okx_v1.src.infrastructure._types import MarketClient
from api_okx_v1.src.infrastructure.consts import OkxMarketConsts
from api_okx_v1.src.infrastructure.gateways.base import BaseQuerySet


class OkxMarketService(
    BaseQuerySet[MarketClient, OkxMarketConsts], 
    IOkxMarketData
):
    def __init__(
        self, 
        market_client: MarketClient, 
        consts: OkxMarketConsts
    ) -> None:
        self._client = market_client
        self._consts = consts

    async def get_candlesticks(
        self, 
        params: GetPriceDataDTO
    ) -> dict[str, Any]:
        return await self.get(
            endpoint=self._consts.GET_CANDLESTICKS, 
            params=await self._prepare_query_params(params)
        )

    async def get_candlesticks_history(
        self, 
        params: GetPriceDataDTO
    ) -> dict[str, Any]:
        return await self.get(
            endpoint=self._consts.GET_CANDLESTICKS_HISTORY, 
            params=await self._prepare_query_params(params)
        )

    async def get_ticker(
        self, 
        instId: str
    ) -> dict[str, Any]:
        return await self.get(
            endpoint=f"{self._consts.GET_TICKER}",
            params={"instId": instId.upper()}
        )

    async def get_mark_price(
        self, 
        params: GetMarketPriceDTO
    ) -> dict[str, Any]:
        return await self.get(
            endpoint=self._consts.GET_MARK_PRICE, 
            params=await self._prepare_query_params(params)
        )

    async def get_instruments(
        self, 
        params: GetInstrumentsDTO
    ) -> dict[str, Any]:
        return await self.get(
            endpoint=self._consts.GET_INSTRUMENTS, 
            params=await self._prepare_query_params(params)
        )
