from typing import Any

from dishka.integrations.faststream import FromDishka, inject
from faststream.rabbit import RabbitRouter

from api_okx_v1.src.application.dto.market import (
    GetInstrumentsDTO,
    GetMarketPriceDTO,
    GetPriceDataDTO
)
from api_okx_v1.src.application.interactors.market import (
    GetCandlesticksInteractor,
    GetCandlesticksHistoryInteractor,
    GetInstrumentsInteractor,
    GetMarketPriceInteractor,
    GetTickerInteractor
)


controller = RabbitRouter(prefix="okx_api")


class OkxApiRoutes:
    @controller.subscriber("get_candlesticks")
    @controller.publisher("send_candlesticks")
    @inject
    async def candlesticks(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetCandlesticksInteractor],
    ) -> dict[str, Any]:
        dto = GetPriceDataDTO(**params)
        return await interactor(dto)

    @controller.subscriber("get_candlesticks_history")
    @controller.publisher("send_candlesticks_history")
    @inject
    async def candlesticks_history(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetCandlesticksHistoryInteractor],
    ) -> dict[str, Any]:
        dto = GetPriceDataDTO(**params)
        return await interactor(dto)

    @controller.subscriber("get_instruments")
    @controller.publisher("send_instruments")
    @inject
    async def instruments(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetInstrumentsInteractor],
    ) -> dict[str, Any]:
        dto = GetInstrumentsDTO(**params)
        return await interactor(dto)

    @controller.subscriber("get_instruments")
    @controller.publisher("send_instruments")
    @inject
    async def market_price(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetMarketPriceInteractor],
    ) -> dict[str, Any]:
        dto = GetMarketPriceDTO(**params)
        return await interactor(dto)

    @controller.subscriber("get_instruments")
    @controller.publisher("send_instruments")
    @inject
    async def ticker(
        self,
        instId: str,
        interactor: FromDishka[GetTickerInteractor],
    ) -> dict[str, Any]:
        return await interactor(instId)

