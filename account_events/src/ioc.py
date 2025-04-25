from typing import AsyncIterable

from dishka import Provider, Scope, provide, from_context
from redis.asyncio import Redis
from faststream.rabbit import RabbitBroker

from account_events.src.application import interfaces
from account_events.src.application.interactors import (
    AccountEventsDeleterInteractor,
    AccountEventsSubscriberInteractor,
    AccountEventsUpdaterInteractor,
    WebSocketBootstrapInteractor,
    WebSocketRecoveryInteractor
)
from account_events.src.config import Config
from account_events.src.infrastructure.security import ConfigEncryptionGateway
from account_events.src.infrastructure.websocket import OKXWebsocketsChannelGateway
from account_events.src.infrastructure.redis_storage import ConnectionStorageGateway
from account_events.src.infrastructure.cache import new_redis_client

class AppProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)
    broker = from_context(provides=RabbitBroker, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    async def get_redis_conn(self, config: Config) -> AsyncIterable[Redis]:
        conn = await new_redis_client(config.redis)
        try:
            yield conn
        finally:
            await conn.aclose()

    config_encryption_gateway = provide(
        ConfigEncryptionGateway,
        scope=Scope.REQUEST,
        provides=interfaces.IConfigEncryption, 
    )

    channels_gateway = provide(
        OKXWebsocketsChannelGateway,
        scope=Scope.APP,
        provides=interfaces.IOkxAccountListner
    )

    connection_storage = provide(
        ConnectionStorageGateway,
        scope=Scope.APP,
        provides=interfaces.IConnectionStorage
    )

    create_sub_interactor = provide(AccountEventsSubscriberInteractor, scope=Scope.REQUEST)
    update_sub_interactor = provide(AccountEventsUpdaterInteractor, scope=Scope.REQUEST)
    delete_sub_interactor = provide(AccountEventsDeleterInteractor, scope=Scope.REQUEST)
    recovery_sub_interactor = provide(WebSocketRecoveryInteractor, scope=Scope.APP)
    bootstrap_sub_interactor = provide(WebSocketBootstrapInteractor, scope=Scope.APP)