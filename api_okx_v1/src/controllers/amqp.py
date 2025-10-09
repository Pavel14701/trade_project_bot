from typing import Any

from dishka.integrations.faststream import FromDishka, inject
from faststream.rabbit import RabbitRouter

from api_okx_v1.src.application.dto.market import (
    GetInstrumentsDTO,
    GetMarketPriceDTO,
    GetPriceDataDTO
)
from api_okx_v1.src.application.dto.base import SecretDTO
from api_okx_v1.src.application.interactors.market import (
    GetCandlesticksInteractor,
    GetCandlesticksHistoryInteractor,
    GetInstrumentsInteractor,
    GetMarketPriceInteractor,
    GetTickerInteractor
)
from api_okx_v1.src.application.interactors.trade import (
    GetAccountBalanceInteractor,
    GetOrderListInteractor,
    GetPositionsInteractor,
    SetPositionModeInteractor,
    SetLeverageInteractor,
    GetLeverageInteractor,  
    PlaceOrderInteractor,
    AmendOrderInteractor,
    CancelOrderInteractor,
    ClosePostionsInteractor,
    GetOrderDetailsInteractor
)
from api_okx_v1.src.controllers.base_router import RouterUtils

controller = RabbitRouter(prefix="okx_api")


class OkxMarketRoutes:
    @controller.subscriber(queue="get_candlesticks")
    @controller.publisher(queue="send_candlesticks")
    @inject
    async def candlesticks(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetCandlesticksInteractor],
    ) -> dict[str, Any]:
        dto = GetPriceDataDTO(**params)
        return await interactor(dto)

    @controller.subscriber(queue="get_candlesticks_history")
    @controller.publisher(queue="send_candlesticks_history")
    @inject
    async def candlesticks_history(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetCandlesticksHistoryInteractor],
    ) -> dict[str, Any]:
        dto = GetPriceDataDTO(**params)
        return await interactor(dto)

    @controller.subscriber(queue="get_instruments")
    @controller.publisher(queue="send_instruments")
    @inject
    async def instruments(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetInstrumentsInteractor],
    ) -> dict[str, Any]:
        dto = GetInstrumentsDTO(**params)
        return await interactor(dto)

    @controller.subscriber(queue="get_market_price")
    @controller.publisher(queue="send_market_price")
    @inject
    async def market_price(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetMarketPriceInteractor],
    ) -> dict[str, Any]:
        dto = GetMarketPriceDTO(**params)
        return await interactor(dto)

    @controller.subscriber(queue="get_ticker")
    @controller.publisher(queue="send_ticker")
    @inject
    async def ticker(
        self,
        instId: str,
        interactor: FromDishka[GetTickerInteractor],
    ) -> dict[str, Any]:
        return await interactor(instId)



class OkxTradeRoutes(RouterUtils):
    # TO DO 
    # add a method to extract secrets 
    # from a message
    @controller.subscriber(queue="get_account_balance")
    @controller.publisher(queue="send_account_balance")
    @inject
    async def get_account_balance(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetAccountBalanceInteractor],
    ) -> dict[str, Any]:
        dto = self.construct_many_named(params, classes=[SecretDTO, GetPriceDataDTO])
        return await interactor(dto)

    @controller.subscriber(queue="get_order_list")
    @controller.publisher(queue="send_order_list")
    @inject
    async def get_order_list(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetOrderListInteractor],
    ) -> dict[str, Any]:
        dto = GetPriceDataDTO(**params)
        return await interactor(dto)

    @controller.subscriber(queue="get_positions")
    @controller.publisher(queue="send_positions")
    @inject
    async def get_positions(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetPositionsInteractor],
    ) -> dict[str, Any]:
        dto = GetPriceDataDTO(**params)
        return await interactor(dto)

    @controller.subscriber(queue="get_position_mode")
    @controller.publisher(queue="send_position_mode")
    @inject
    async def get_position_mode(
        self,
        params: dict[str, Any],
        interactor: FromDishka[SetPositionModeInteractor],
    ) -> dict[str, Any]:
        dto = GetPriceDataDTO(**params)
        return await interactor(dto)

    @controller.subscriber(queue="get_set_leverage")
    @controller.publisher(queue="send_set_leverage")
    @inject
    async def get_set_leverage(
        self,
        params: dict[str, Any],
        interactor: FromDishka[SetLeverageInteractor],
    ) -> dict[str, Any]:
        dto = GetPriceDataDTO(**params)
        return await interactor(dto)

    @controller.subscriber(queue="get_get_leverage")
    @controller.publisher(queue="send_get_leverage")
    @inject
    async def get_leverage(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetLeverageInteractor],
    ) -> dict[str, Any]:
        dto = GetPriceDataDTO(**params)
        return await interactor(dto)

    @controller.subscriber(queue="get_place_order")
    @controller.publisher(queue="send_place_order")
    @inject
    async def get_place_order(
        self,
        params: dict[str, Any],
        interactor: FromDishka[PlaceOrderInteractor],
    ) -> dict[str, Any]:
        dto = GetPriceDataDTO(**params)
        return await interactor(dto)

    @controller.subscriber(queue="get_amend_order")
    @controller.publisher(queue="send_amend_order")
    @inject
    async def get_place_order(
        self,
        params: dict[str, Any],
        interactor: FromDishka[AmendOrderInteractor],
    ) -> dict[str, Any]:
        dto = GetPriceDataDTO(**params)
        return await interactor(dto)

    @controller.subscriber(queue="get_cancel_order")
    @controller.publisher(queue="send_cancel_order")
    @inject
    async def get_cancel_order(
        self,
        params: dict[str, Any],
        interactor: FromDishka[CancelOrderInteractor],
    ) -> dict[str, Any]:
        dto = GetPriceDataDTO(**params)
        return await interactor(dto)

    @controller.subscriber(queue="get_close_positions")
    @controller.publisher(queue="send_close_positions")
    @inject
    async def get_close_positions(
        self,
        params: dict[str, Any],
        interactor: FromDishka[ClosePostionsInteractor],
    ) -> dict[str, Any]:
        dto = GetPriceDataDTO(**params)
        return await interactor(dto)

    @controller.subscriber(queue="get_order_details")
    @controller.publisher(queue="send_order_details")
    @inject
    async def get_order_details(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetOrderDetailsInteractor],
    ) -> dict[str, Any]:
        dto = GetPriceDataDTO(**params)
        return await interactor(dto)
