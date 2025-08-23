from typing import Any
from api_okx_v1.src.application.dto.market import (
    GetInstrumentsDTO,
    GetPriceDataDTO,
    GetMarketPriceDTO
)
from api_okx_v1.src.application.interfaces import IOkxMarketData
from api_okx_v1.src.infrastructure._types import MarketClient
from api_okx_v1.src.infrastructure.consts import OkxMarketConsts


class OkxMarketService(IOkxMarketData):
    def __init__(
        self, 
        market_client: MarketClient, 
        consts: OkxMarketConsts
    ) -> None:
        self._client = market_client
        self._consts = consts

    async def _prepare_query_params(
        self, 
        dto: GetPriceDataDTO|GetMarketPriceDTO|GetInstrumentsDTO
    ) -> dict[str, Any]:
        return {k: v for k, v in dto.to_dict().items() if v is not None}

    async def _get(
        self, 
        endpoint: str, 
        params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        response = await self._client.get(
            url=f"{self._consts.BASE_URL}{endpoint}",
            params=params,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def get_candlesticks(
        self, 
        params: GetPriceDataDTO
    ) -> dict[str, Any]:
        return await self._get(
            endpoint=self._consts.GET_CANDLESTICKS, 
            params=await self._prepare_query_params(params)
        )

    async def get_candlesticks_history(
        self, 
        params: GetPriceDataDTO
    ) -> dict[str, Any]:
        return await self._get(
            endpoint=self._consts.GET_CANDLESTICKS_HISTORY, 
            params=await self._prepare_query_params(params)
        )

    async def get_ticker(
        self, 
        instId: str
    ) -> dict[str, Any]:
        return await self._get(
            endpoint=f"{self._consts.GET_TICKER}",
            params={"instId": instId.upper()}
        )

    async def get_mark_price(
        self, 
        params: GetMarketPriceDTO
    ) -> dict[str, Any]:
        return await self._get(
            endpoint=self._consts.GET_MARK_PRICE, 
            params=await self._prepare_query_params(params)
        )

    async def get_instruments(
        self, 
        params: GetInstrumentsDTO
    ) -> dict[str, Any]:
        return await self._get(
            endpoint=self._consts.GET_INSTRUMENTS, 
            params=await self._prepare_query_params(params)
        )
