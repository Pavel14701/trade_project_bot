"""
Provides a concrete implementation of the OKX Market Data service interface.

This module defines the `OkxMarketService` class, which extends the generic `BaseQuerySet`
and implements the `IOkxMarketData` interface. It encapsulates interactions with OKX market
data endpoints, including candlestick retrieval, ticker information, mark price, and instrument listings.

Key Responsibilities:
- Prepare and send authenticated HTTP requests to OKX market endpoints.
- Serialize request parameters using DTOs.
- Provide high-level methods for accessing market data.

Dependencies:
- `BaseQuerySet`: Abstract base class for HTTP request execution and signing.
- DTOs from `application.dto.market`: Define structured request payloads.
- `IOkxMarketData`: Interface defining expected market data operations.
- `MarketClient`: Asynchronous HTTP client for market API calls.
- `OkxMarketConsts`: Constants specific to market data endpoints.
"""


from typing import Any
from application.dto.market import (
    GetInstrumentsDTO,
    GetPriceDataDTO,
    GetMarketPriceDTO
)
from application.interfaces import IOkxMarketData
from infrastructure._types import MarketClient
from infrastructure.consts import OkxMarketConsts
from infrastructure.gateways.base import BaseQuerySet


class OkxMarketService(BaseQuerySet[MarketClient, OkxMarketConsts], IOkxMarketData):
    """
    Service class for interacting with OKX Market Data API endpoints.

    Implements the `IOkxMarketData` interface and provides methods to query
    candlestick data, ticker information, mark prices, and available instruments.

    Inherits from `BaseQuerySet` to leverage shared request logic and signing.
    """

    def __init__(
        self, 
        market_client: MarketClient, 
        consts: OkxMarketConsts
    ) -> None:
        """
        Initializes the market service with a client and constants.

        Args:
            market_client (MarketClient): Asynchronous HTTP client for market API calls.
            consts (OkxMarketConsts): Configuration constants for endpoint paths.
        """
        self._client = market_client
        self._consts = consts

    async def get_candlesticks(
        self, 
        params: GetPriceDataDTO
    ) -> dict[str, Any]:
        """
        Retrieves current candlestick data for a specified instrument.

        Args:
            params (GetPriceDataDTO): Parameters including instrument ID, time frame, and limit.

        Returns:
            dict[str, Any]: Candlestick data including open, high, low, close, and volume.
        """
        return await self.get(
            endpoint=self._consts.GET_CANDLESTICKS, 
            params=await self._prepare_query_params(params)
        )

    async def get_candlesticks_history(
        self, 
        params: GetPriceDataDTO
    ) -> dict[str, Any]:
        """
        Retrieves historical candlestick data for a specified instrument.

        Args:
            params (GetPriceDataDTO): Parameters including instrument ID, time frame, and date range.

        Returns:
            dict[str, Any]: Historical candlestick data.
        """
        return await self.get(
            endpoint=self._consts.GET_CANDLESTICKS_HISTORY, 
            params=await self._prepare_query_params(params)
        )

    async def get_ticker(
        self, 
        instId: str
    ) -> dict[str, Any]:
        """
        Retrieves real-time ticker information for a specific instrument.

        Args:
            instId (str): Instrument identifier (e.g., "BTC-USDT").

        Returns:
            dict[str, Any]: Ticker data including last price, bid/ask, and volume.
        """
        return await self.get(
            endpoint=f"{self._consts.GET_TICKER}",
            params={"instId": instId.upper()}
        )

    async def get_mark_price(
        self, 
        params: GetMarketPriceDTO
    ) -> dict[str, Any]:
        """
        Retrieves the current mark price for a specified instrument.

        Args:
            params (GetMarketPriceDTO): Parameters including instrument ID.

        Returns:
            dict[str, Any]: Mark price data used for margin calculations.
        """
        return await self.get(
            endpoint=self._consts.GET_MARK_PRICE, 
            params=await self._prepare_query_params(params)
        )

    async def get_instruments(
        self, 
        params: GetInstrumentsDTO
    ) -> dict[str, Any]:
        """
        Retrieves a list of available trading instruments.

        Args:
            params (GetInstrumentsDTO): Parameters for filtering instruments (e.g., type, underlying).

        Returns:
            dict[str, Any]: List of instruments with metadata such as symbol, type, and precision.
        """
        return await self.get(
            endpoint=self._consts.GET_INSTRUMENTS, 
            params=await self._prepare_query_params(params)
        )
