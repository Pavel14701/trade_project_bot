from typing import AsyncIterable

from dishka import Provider, Scope, from_context, provide # type: ignore
from faststream.rabbit import RabbitBroker # type: ignore
from redis.asyncio import Redis # type: ignore

from application import interfaces
from application.interactors import (
    AccountEventsDeleterInteractor,
    AccountEventsSubscriberInteractor,
    AccountEventsUpdaterInteractor,
    WebSocketBootstrapInteractor,
    WebSocketRecoveryInteractor,
)
from config import Config
from infrastructure.cache import new_redis_client
from infrastructure.redis_storage import ConnectionStorageGateway
from infrastructure.security import ConfigEncryptionGateway
from infrastructure.websocket import OKXWebsocketsChannelGateway


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

    create_sub_interactor = provide(
        source=AccountEventsSubscriberInteractor, 
        scope=Scope.REQUEST
    )
    update_sub_interactor = provide(
        source=AccountEventsUpdaterInteractor, 
        scope=Scope.REQUEST
    )
    delete_sub_interactor = provide(
        source=AccountEventsDeleterInteractor, 
        scope=Scope.REQUEST
    )
    recovery_sub_interactor = provide(
        source=WebSocketRecoveryInteractor,
        scope=Scope.APP
    )
    bootstrap_sub_interactor = provide(
        source=WebSocketBootstrapInteractor,
        scope=Scope.APP
    )