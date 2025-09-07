from typing import AsyncGenerator

from dishka import Provider, Scope, provide # type: ignore

from api_okx_v1.src.infrastructure.http_sessions import client_factory, MarketClientPool
from api_okx_v1.src.infrastructure._types import (
    MarketClient,
    PrivateClient
)


class OkxApiProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_market_client_pool() -> AsyncGenerator[MarketClientPool, None]:
        pool = MarketClientPool(pool_size=5, rate_limit=20)
        try:
            yield pool
        finally:
            await pool.aclose()    

    @provide(scope=Scope.APP)
    async def provide_market_client(self, pool: MarketClientPool) -> AsyncGenerator[MarketClient, None]:
        async with pool.get() as client:
            yield client

    @provide(scope=Scope.REQUEST)
    async def provide_private_client(self) -> AsyncGenerator[PrivateClient, None]:
        async for client in client_factory():
            yield client
