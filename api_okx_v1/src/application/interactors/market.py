from typing import Any

from api_okx_v1.src.application.interfaces import ( 
    IOkxMarketData, 
    IOkxExcHandler
)
from api_okx_v1.src.application.dto.market import (
    GetMarketPriceDTO, 
    GetPriceDataDTO, 
    GetInstrumentsDTO,
)


class GetCandlesticksInteractor:
    def __init__(
        self,
        exc_handler: IOkxExcHandler,
        market_repo: IOkxMarketData
    ) -> None:
        self._exc_handler = exc_handler
        self._market_repo = market_repo
    
    async def __call__(self, params: GetPriceDataDTO) -> dict[str, Any]:
        return await self._market_repo.get_candlesticks(params=params)


class GetCandlesticksHistoryInteractor:
    def __init__(
        self,
        exc_handler: IOkxExcHandler,
        market_repo: IOkxMarketData
    ) -> None:
        self._exc_handler = exc_handler
        self._market_repo = market_repo

    async def __call__(self, params: GetPriceDataDTO) -> dict[str, Any]:
        return await self._market_repo.get_candlesticks_history(params=params)


class GetTickerInteractor:
    def __init__(
        self,
        exc_handler: IOkxExcHandler,
        market_repo: IOkxMarketData
    ) -> None:
        self._exc_handler = exc_handler
        self._market_repo = market_repo

    async def __call__(self, instId: str) -> dict[str, Any]:
        return await self._market_repo.get_ticker(instId=instId)


class GetMarketPriceInteractor:
    def __init__(
        self,
        exc_handler: IOkxExcHandler,
        market_repo: IOkxMarketData
    ) -> None:
        self._exc_handler = exc_handler
        self._market_repo = market_repo

    async def __call__(self, params: GetMarketPriceDTO) -> dict[str, Any]:
        return await self._market_repo.get_mark_price(params=params)


class GetInstrumentsInteractor:
    def __init__(
        self,
        exc_handler: IOkxExcHandler,
        market_repo: IOkxMarketData
    ) -> None:
        self._exc_handler = exc_handler
        self._market_repo = market_repo

    async def __call__(self, params: GetInstrumentsDTO) -> dict[str, Any]:
        return await self._market_repo.get_instruments(params=params)

