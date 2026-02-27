from abc import ABC
from typing import Any

from application.dto.market import (
    GetInstrumentsDTO,
    GetMarketPriceDTO,
    GetPriceDataDTO,
)
from application.interfaces import IOkxExcHandler, IOkxMarketData


class BaseMarketDTO(ABC):
    def __init__(
        self,
        exc_handler: IOkxExcHandler,
        market_repo: IOkxMarketData
    ) -> None:
        self._exc_handler = exc_handler
        self._market_repo = market_repo


class GetCandlesticksInteractor(BaseMarketDTO):
    async def __call__(self, params: GetPriceDataDTO) -> dict[str, Any]:
        return await self._market_repo.get_candlesticks(params=params)


class GetCandlesticksHistoryInteractor(BaseMarketDTO):
    async def __call__(self, params: GetPriceDataDTO) -> dict[str, Any]:
        return await self._market_repo.get_candlesticks_history(params=params)


class GetTickerInteractor(BaseMarketDTO):
    async def __call__(self, instId: str) -> dict[str, Any]:
        return await self._market_repo.get_ticker(instId=instId)


class GetMarketPriceInteractor(BaseMarketDTO):
    async def __call__(self, params: GetMarketPriceDTO) -> dict[str, Any]:
        return await self._market_repo.get_mark_price(params=params)


class GetInstrumentsInteractor(BaseMarketDTO):
    async def __call__(self, params: GetInstrumentsDTO) -> dict[str, Any]:
        return await self._market_repo.get_instruments(params=params)