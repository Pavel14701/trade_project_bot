"""
Defines RabbitMQ-based message handlers for OKX market and trading operations using FastStream and Dishka.

This module contains two main route classes:

- `OkxMarketRoutes`: Handles market data queries such as candlesticks, instruments, and prices.
- `OkxTradeRoutes`: Handles trading operations including placing orders, retrieving balances, and managing positions.

Each method is decorated with FastStream's `@subscriber` and `@publisher` to bind queues for input and output.
Dependencies are injected via Dishka's `@inject` and `FromDishka` to decouple business logic from transport.

DTOs are used to validate and structure incoming payloads, and interactors encapsulate domain-specific logic.

Usage:
    - Messages are consumed from RabbitMQ queues.
    - Payloads are parsed into DTOs.
    - Interactors are invoked with validated data.
    - Responses are published to output queues.

This design promotes separation of concerns, testability, and scalability in a microservice architecture.
"""

from typing import Any

from dishka.integrations.faststream import FromDishka, inject
from faststream.rabbit import RabbitRouter

from api_okx_v1.src.application.dto.market import (
    GetInstrumentsDTO,
    GetMarketPriceDTO,
    GetPriceDataDTO
)
from api_okx_v1.src.application.dto.base import SecretDTO
from api_okx_v1.src.application.dto.trade import (
    CancelOrderDTO, 
    ClosePositionsDTO, 
    GetBalanceDTO, 
    GetLeverageDTO, 
    GetOrderDetailsDTO, 
    GetOrderListDTO, 
    PlaceOrderDTO, 
    SetLeverageDTO
)
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
from api_okx_v1.src.application.interfaces import AmendOrderDTO
from api_okx_v1.src.controllers.base_router import RouterUtils


controller = RabbitRouter(prefix="okx_api")


class OkxMarketRoutes:
    """
    Defines RabbitMQ subscribers and publishers for OKX market-related operations.

    Each method in this class handles a specific market data request, such as candlestick retrieval,
    instrument listing, or price queries. Incoming messages are parsed into DTOs and passed to
    corresponding interactors, which encapsulate business logic.

    Dependencies are injected using Dishka's `FromDishka` mechanism.
    """

    @controller.subscriber(queue="get_candlesticks")
    @controller.publisher(queue="send_candlesticks")
    @inject
    async def candlesticks(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetCandlesticksInteractor],
    ) -> dict[str, Any]:
        """
        Handles incoming requests for current candlestick data.

        Subscribes to the "get_candlesticks" queue and publishes results to "send_candlesticks".
        Parses incoming parameters into `GetPriceDataDTO` and delegates to `GetCandlesticksInteractor`.

        Args:
            params (dict[str, Any]): Raw message payload containing candlestick query parameters.
            interactor (FromDishka[GetCandlesticksInteractor]): Injected business logic handler.

        Returns:
            dict[str, Any]: Candlestick data response.
        """
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
        """
        Retrieves historical candlestick data.

        Subscribes to "get_candlesticks_history" and publishes to "send_candlesticks_history".
        Converts parameters into `GetPriceDataDTO` and invokes `GetCandlesticksHistoryInteractor`.

        Args:
            params (dict[str, Any]): Historical query parameters.
            interactor (FromDishka[GetCandlesticksHistoryInteractor]): Logic handler.

        Returns:
            dict[str, Any]: Historical candlestick data.
        """
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
        """
        Fetches available trading instruments from OKX.

        Subscribes to "get_instruments" and publishes to "send_instruments".
        Converts parameters into `GetInstrumentsDTO` and invokes `GetInstrumentsInteractor`.

        Args:
            params (dict[str, Any]): Instrument query parameters.
            interactor (FromDishka[GetInstrumentsInteractor]): Logic handler.

        Returns:
            dict[str, Any]: List of instruments.
        """
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
        """
        Retrieves current market price for a given instrument.

        Subscribes to "get_market_price" and publishes to "send_market_price".
        Converts parameters into `GetMarketPriceDTO` and invokes `GetMarketPriceInteractor`.

        Args:
            params (dict[str, Any]): Market price query parameters.
            interactor (FromDishka[GetMarketPriceInteractor]): Logic handler.

        Returns:
            dict[str, Any]: Market price data.
        """
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
        """
        Retrieves ticker information for a specific instrument.

        Subscribes to "get_ticker" and publishes to "send_ticker".
        Passes instrument ID directly to `GetTickerInteractor`.

        Args:
            instId (str): Instrument identifier.
            interactor (FromDishka[GetTickerInteractor]): Logic handler.

        Returns:
            dict[str, Any]: Ticker data.
        """
        return await interactor(instId)



class OkxTradeRoutes(RouterUtils):
    """
    Defines RabbitMQ subscribers and publishers for OKX trading operations.

    Each method handles a specific trading action such as placing orders, retrieving balances,
    or modifying positions. Incoming messages are parsed into DTOs and passed to interactors
    that encapsulate the trading logic.

    Uses Dishka for dependency injection and RouterUtils for DTO construction.
    """

    @controller.subscriber(queue="get_account_balance")
    @controller.publisher(queue="send_account_balance")
    @inject
    async def get_account_balance(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetAccountBalanceInteractor],
    ) -> dict[str, Any]:
        """
        Retrieves account balance for a specific currency.

        Subscribes to "get_account_balance" and publishes to "send_account_balance".
        Constructs `SecretDTO` from parameters and invokes `GetAccountBalanceInteractor`.

        Args:
            params (dict[str, Any]): Contains 'ccy' and secret credentials.
            interactor (FromDishka[GetAccountBalanceInteractor]): Logic handler.

        Returns:
            dict[str, Any]: Account balance data.
        """
        dto = self.construct(params, SecretDTO)
        return await interactor(
            ccy=params['ccy'],
            secret=dto
        )

    @controller.subscriber(queue="get_order_list")
    @controller.publisher(queue="send_order_list")
    @inject
    async def get_order_list(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetOrderListInteractor],
    ) -> dict[str, Any]:
        """
        Retrieves a list of active or historical orders for the authenticated user.

        Subscribes to "get_order_list" and publishes to "send_order_list".
        Constructs both `GetOrderListDTO` and `SecretDTO` from the incoming parameters,
        and passes them to `GetOrderListInteractor`.

        Args:
            params (dict[str, Any]): Contains filtering options and authentication secrets.
            interactor (FromDishka[GetOrderListInteractor]): Business logic handler.

        Returns:
            dict[str, Any]: List of orders matching the query.
        """
        dto = self.construct_many_named(
            data=params,
            classes=[GetOrderListDTO, SecretDTO]
        )
        return await interactor(
            getattr(dto, "GetOrderListDTO"), 
            getattr(dto, "SecretDTO")
        )

    @controller.subscriber(queue="get_positions")
    @controller.publisher(queue="send_positions")
    @inject
    async def get_positions(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetPositionsInteractor],
    ) -> dict[str, Any]:
        """
        Fetches current open positions for the authenticated account.

        Subscribes to "get_positions" and publishes to "send_positions".
        Constructs `GetBalanceDTO` and `SecretDTO` from parameters and invokes `GetPositionsInteractor`.

        Args:
            params (dict[str, Any]): Includes currency and secret credentials.
            interactor (FromDishka[GetPositionsInteractor]): Business logic handler.

        Returns:
            dict[str, Any]: Position data including size, margin, and instrument info.
        """
        dto = self.construct_many_named(
            data=params,
            classes=[GetBalanceDTO, SecretDTO]
        )
        return await interactor(
            getattr(dto, "GetBalanceDTO"), 
            getattr(dto, "SecretDTO")
        )

    @controller.subscriber(queue="get_position_mode")
    @controller.publisher(queue="send_position_mode")
    @inject
    async def get_position_mode(
        self,
        params: dict[str, Any],
        interactor: FromDishka[SetPositionModeInteractor],
    ) -> dict[str, Any]:
        """
        Retrieves or sets the current position mode (e.g., net vs isolated).

        Subscribes to "get_position_mode" and publishes to "send_position_mode".
        Constructs `SecretDTO` and passes `posMode` directly to `SetPositionModeInteractor`.

        Args:
            params (dict[str, Any]): Includes 'posMode' and secret credentials.
            interactor (FromDishka[SetPositionModeInteractor]): Business logic handler.

        Returns:
            dict[str, Any]: Confirmation of position mode status.
        """
        dto = self.construct(
            data=params,
            cls=SecretDTO
        )
        return await interactor(
            posMode=params['posMode'], 
            secret=dto
        )

    @controller.subscriber(queue="get_set_leverage")
    @controller.publisher(queue="send_set_leverage")
    @inject
    async def get_set_leverage(
        self,
        params: dict[str, Any],
        interactor: FromDishka[SetLeverageInteractor],
    ) -> dict[str, Any]:
        """
        Sets leverage for a specific instrument or position.

        Subscribes to "get_set_leverage" and publishes to "send_set_leverage".
        Constructs `SetLeverageDTO` and `SecretDTO` and invokes `SetLeverageInteractor`.

        Args:
            params (dict[str, Any]): Includes leverage settings and authentication.
            interactor (FromDishka[SetLeverageInteractor]): Business logic handler.

        Returns:
            dict[str, Any]: Confirmation of leverage update.
        """
        dto = self.construct_many_named(
            data=params,
            classes=[SetLeverageDTO, SecretDTO]
        )
        return await interactor(
            getattr(dto, "SetLeverageDTO"), 
            getattr(dto, "SecretDTO")
        )

    @controller.subscriber(queue="get_get_leverage")
    @controller.publisher(queue="send_get_leverage")
    @inject
    async def get_leverage(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetLeverageInteractor],
    ) -> dict[str, Any]:
        """
        Retrieves current leverage settings for a given instrument or account.

        Subscribes to "get_get_leverage" and publishes to "send_get_leverage".
        Constructs `GetLeverageDTO` and `SecretDTO` and invokes `GetLeverageInteractor`.

        Args:
            params (dict[str, Any]): Includes instrument ID and secret credentials.
            interactor (FromDishka[GetLeverageInteractor]): Business logic handler.

        Returns:
            dict[str, Any]: Current leverage configuration.
        """
        dto = self.construct_many_named(
            data=params,
            classes=[GetLeverageDTO, SecretDTO]
        )
        return await interactor(
            getattr(dto, "GetLeverageDTO"), 
            getattr(dto, "SecretDTO")
        )

    @controller.subscriber(queue="get_place_order")
    @controller.publisher(queue="send_place_order")
    @inject
    async def get_place_order(
        self,
        params: dict[str, Any],
        interactor: FromDishka[PlaceOrderInteractor],
    ) -> dict[str, Any]:
        """
        Places a new order on the OKX trading platform.

        Subscribes to "get_place_order" and publishes to "send_place_order".
        Constructs `PlaceOrderDTO` and `SecretDTO` and invokes `PlaceOrderInteractor`.

        Args:
            params (dict[str, Any]): Includes order details and authentication.
            interactor (FromDishka[PlaceOrderInteractor]): Business logic handler.

        Returns:
            dict[str, Any]: Confirmation and details of the placed order.
        """
        dto = self.construct_many_named(
            data=params,
            classes=[PlaceOrderDTO, SecretDTO]
        )
        return await interactor(
            getattr(dto, "PlaceOrderDTO"), 
            getattr(dto, "SecretDTO")
        )

    @controller.subscriber(queue="get_amend_order")
    @controller.publisher(queue="send_amend_order")
    @inject
    async def get_amend_order(
        self,
        params: dict[str, Any],
        interactor: FromDishka[AmendOrderInteractor],
    ) -> dict[str, Any]:
        """
        Modifies an existing order (e.g., price, quantity).

        Subscribes to "get_amend_order" and publishes to "send_amend_order".
        Constructs `AmendOrderDTO` and `SecretDTO` and invokes `AmendOrderInteractor`.

        Args:
            params (dict[str, Any]): Includes amendment details and authentication.
            interactor (FromDishka[AmendOrderInteractor]): Business logic handler.

        Returns:
            dict[str, Any]: Confirmation of order amendment.
        """
        dto = self.construct_many_named(
            data=params,
            classes=[AmendOrderDTO, SecretDTO]
        )
        return await interactor(
            getattr(dto, "AmendOrderDTO"), 
            getattr(dto, "SecretDTO")
        )

    @controller.subscriber(queue="get_cancel_order")
    @controller.publisher(queue="send_cancel_order")
    @inject
    async def get_cancel_order(
        self,
        params: dict[str, Any],
        interactor: FromDishka[CancelOrderInteractor],
    ) -> dict[str, Any]:
        """
        Cancels an active order on the OKX platform.

        Subscribes to "get_cancel_order" and publishes to "send_cancel_order".
        Constructs `CancelOrderDTO` and `SecretDTO` and invokes `CancelOrderInteractor`.

        Args:
            params (dict[str, Any]): Includes order ID and authentication.
            interactor (FromDishka[CancelOrderInteractor]): Business logic handler.

        Returns:
            dict[str, Any]: Confirmation of cancellation.
        """
        dto = self.construct_many_named(
            data=params,
            classes=[CancelOrderDTO, SecretDTO]
        )
        return await interactor(
            getattr(dto, "CancelOrderDTO"), 
            getattr(dto, "SecretDTO")
        )

    @controller.subscriber(queue="get_close_positions")
    @controller.publisher(queue="send_close_positions")
    @inject
    async def get_close_positions(
        self,
        params: dict[str, Any],
        interactor: FromDishka[ClosePostionsInteractor],
    ) -> dict[str, Any]:
        """
        Closes open positions for the authenticated account.

        Subscribes to "get_close_positions" and publishes to "send_close_positions".
        Constructs `ClosePositionsDTO` and `SecretDTO` and invokes `ClosePostionsInteractor`.

        Args:
            params (dict[str, Any]): Includes position details and authentication.
            interactor (FromDishka[ClosePostionsInteractor]): Business logic handler.

        Returns:
            dict[str, Any]: Confirmation of closed positions.
        """
        dto = self.construct_many_named(
            data=params,
            classes=[ClosePositionsDTO, SecretDTO]
        )
        return await interactor(
            getattr(dto, "ClosePositionsDTO"), 
            getattr(dto, "SecretDTO")
        )

    @controller.subscriber(queue="get_order_details")
    @controller.publisher(queue="send_order_details")
    @inject
    async def get_order_details(
        self,
        params: dict[str, Any],
        interactor: FromDishka[GetOrderDetailsInteractor],
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific order.

        Subscribes to "get_order_details" and publishes to "send_order_details".
        Constructs `GetOrderDetailsDTO` and `SecretDTO` and invokes `GetOrderDetailsInteractor`.

        Args:
            params (dict[str, Any]): Includes order ID and authentication.
            interactor (FromDishka[GetOrderDetailsInteractor]): Business logic handler.

        Returns:
            dict[str, Any]: Detailed order information.
        """
        dto = self.construct_many_named(
            data=params,
            classes=[GetOrderDetailsDTO, SecretDTO]
        )
        return await interactor(
            getattr(dto, "GetOrderDetailsDTO"), 
            getattr(dto, "SecretDTO")
        )