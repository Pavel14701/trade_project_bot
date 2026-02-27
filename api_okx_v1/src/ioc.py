from typing import AsyncGenerator

from dishka import Provider, Scope, from_context, provide  # type: ignore

from application import interfaces
from config import AppConfig, Config
from infrastructure._types import MarketClient, PrivateClient
from infrastructure.consts import (
    OkxGridConsts,
    OkxMarketConsts,
    OkxTradeConsts,
)
from infrastructure.gateways.grid import OkxGridService
from infrastructure.gateways.market import OkxMarketService
from infrastructure.gateways.trade import OkxTradeService
from infrastructure.http_sessions import MarketClientPool, client_factory
from infrastructure.security import SecurityGateway, SignatureGateway


class OkxApiProvider(Provider):
    market_consts = from_context(provides=OkxMarketConsts, scope=Scope.APP)
    trade_consts = from_context(provides=OkxTradeConsts, scope=Scope.APP)
    grid_consts = from_context(provides=OkxGridConsts, scope=Scope.APP)
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def provide_market_client_pool(
        self, 
        config: AppConfig
    ) -> AsyncGenerator[MarketClientPool, None]:
        pool = MarketClientPool(
            pool_size=config.pool_size, 
            rate_limit=config.rate_limit
        )
        try:
            yield pool
        finally:
            await pool.aclose()    

    @provide(scope=Scope.APP)
    async def provide_market_client(
        self, 
        pool: MarketClientPool
    ) -> AsyncGenerator[MarketClient, None]:
        async with pool.get() as client:
            yield client

    @provide(scope=Scope.REQUEST)
    async def provide_private_client(
        self
    ) -> AsyncGenerator[PrivateClient, None]:
        async for client in client_factory():
            yield client

    security_gateway = provide(
        SecurityGateway,
        scope=Scope.REQUEST,
        provides=interfaces.ISecurity, 
    )

    signature_gateway = provide(
        SignatureGateway,
        scope=Scope.REQUEST,
        provides=interfaces.ISignature
    )

    market_api_gateway = provide(
        OkxMarketService,
        scope=Scope.REQUEST,
        provides=interfaces.IOkxMarketData
    )

    trade_api_gateway = provide(
        OkxTradeService,
        scope=Scope.REQUEST,
        provides=interfaces.IOkxTrade
    )

    grid_api_gateway = provide(
        OkxGridService,
        scope=Scope.REQUEST,
        provides=interfaces.IOkxGridTrade
    )