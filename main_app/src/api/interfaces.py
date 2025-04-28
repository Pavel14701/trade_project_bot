from typing import Any, Protocol

from main_app.src.api.dto import (
    MarkPriceRequestDto, 
    PriceDataRequestDTO
)

class IOkxTrade(Protocol):
    pass

class IOkxMarketData(Protocol):
    async def get_candlesticks(self, params: PriceDataRequestDTO) -> dict[str, Any]: 
    # https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-candlesticks
        ...

    async def get_candlesticks_history(self, params: PriceDataRequestDTO) -> dict[str, Any]:
    # https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-candlesticks-history
        ...

    async def get_ticker(self, ) -> dict[str, Any]:
        # https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-ticker
        ...

    async def get_mark_price(self, params: MarkPriceRequestDto) -> dict[str, str]:
    # https://www.okx.com/docs-v5/en/#public-data-rest-api-get-mark-price
        ...

    async def get_instruments(self, inst_id: str) -> dict[str, Any]:
    # https://www.okx.com/docs-v5/en/#public-data-rest-api-get-instruments
        ...


class IAsyncRequests(Protocol):
    pass