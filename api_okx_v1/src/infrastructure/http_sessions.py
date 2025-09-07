from contextlib import asynccontextmanager
from typing import (
    Any, 
    AsyncGenerator, 
)

from aiolimiter import AsyncLimiter
from httpx import Limits

from api_okx_v1.src.infrastructure._types import (
    MarketClient, 
    PrivateClient,
)


class MarketClientPool:
    """
    A simplified client pool using HTTPX's built-in connection management
    and aiolimiter for rate limiting.

    Attributes:
        _limiter (AsyncLimiter): Controls the rate of outgoing requests.
        _client (MarketClient): Shared HTTP client with connection pooling.
    """

    def __init__(self, pool_size: int = 5, rate_limit: int = 20) -> None:
        self._limiter = AsyncLimiter(rate_limit, time_period=1.0)
        self._client = MarketClient(
            http2=True,
            limits=Limits(
                max_keepalive_connections=pool_size,
                max_connections=pool_size
            )
        )

    @asynccontextmanager
    async def get(self) -> AsyncGenerator[MarketClient, Any]:
        """
        Context manager that yields the shared HTTP client,
        enforcing rate limits before access.

        Usage:
            async with pool.get() as client:
                await client.get(...)
        """
        async with self._limiter:
            yield self._client

    async def aclose(self) -> None:
        """
        Gracefully closes the shared HTTP client.
        Should be called during application shutdown.
        """
        await self._client.aclose()


async def client_factory() -> AsyncGenerator[PrivateClient, Any]:
    """
    Asynchronous factory function that yields an HTTPX AsyncClient instance.

    This function creates an `httpx.AsyncClient` configured to support HTTP/2, 
    and yields it for use in asynchronous operations such as making HTTP requests. 
    Once the client is no longer needed, it ensures proper cleanup by closing the 
    connection gracefully.

    Yields:
        httpx.AsyncClient: An instance of HTTPX's asynchronous client.

    """
    async with PrivateClient(http2=True) as client:
        yield client