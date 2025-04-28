from typing import AsyncIterable
from uuid import uuid4

from argon2 import PasswordHasher
from cryptography.fernet import Fernet
from dishka import Provider, Scope, AnyOf, from_context, provide
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from redis.asyncio import Redis

from main_app.src.application import interfaces
from main_app.src.application.interactors import (
    GetOkxListnerConfigsInteractor,
    GetUserInteractor,
    LoginInteractor,
    SignupInteractor,
    SaveOkxListnerConfigInteractor
)
from main_app.src.config import Config, SecretConfig
from main_app.src.infrastructure.factories.redis import new_redis_client
from main_app.src.infrastructure.factories.postgres import new_session_maker
from main_app.src.infrastructure.repositories.cookies import (
    CookieRepo
)
from main_app.src.infrastructure.repositories.exc import (
    ExceptionHandlersRepo
)
from main_app.src.infrastructure.repositories.sessions import (
    GuestSessionBackend,
    RedisSessionBackend
)
from main_app.src.infrastructure.repositories.security import (
    ConfigEncryptionRepo,
    SecurityRepo
)
from main_app.src.infrastructure.repositories.user import (
    UserRepo
)


class AppProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)
    broker = from_context(provides=RabbitBroker, scope=Scope.APP)
    password_hasher = from_context(provides=PasswordHasher, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_uuid_generator(self) -> interfaces.UUIDGenerator:
        return uuid4

    @provide(scope=Scope.REQUEST)
    async def get_redis_conn(self, config: Config) -> AsyncIterable[Redis]:
        conn = await new_redis_client(config.redis)
        try:
            yield conn
        finally:
            await conn.aclose()

    @provide(scope=Scope.APP)
    def get_cipher(self, config: Config) -> Fernet:
        return Fernet(config.secret.config_secret_key)

    @provide(scope=Scope.APP)
    def get_secret_config(self, config: Config) -> SecretConfig:
        return config.secret

    @provide(scope=Scope.APP)
    def get_session_maker(
        self, 
        config: Config
    ) -> async_sessionmaker[AsyncSession]:
        return new_session_maker(config.postgres)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, 
        session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[
        AnyOf[AsyncSession, interfaces.ISession,]
    ]:
        async with session_maker() as session:
            yield session

    get_cookie_repo = provide(
        CookieRepo,
        scope=Scope.REQUEST,
        provides=interfaces.ICookieBackend, 
    )

    get_exc_handler_repo = provide(
        ExceptionHandlersRepo,
        scope=Scope.REQUEST,
        provides=interfaces.IErrorHandler
    )

    get_session_backend = provide(
        RedisSessionBackend,
        scope=Scope.REQUEST,
        provides=interfaces.ISessionBackend
    )

    get_guest_session_backend = provide(
        GuestSessionBackend,
        scope=Scope.REQUEST,
        provides=interfaces.IGuestSessionBackend
    )

    get_guest_session_backend = provide(
        ConfigEncryptionRepo,
        scope=Scope.REQUEST,
        provides=interfaces.IConfigEncryption
    )

    get_guest_session_backend = provide(
        SecurityRepo,
        scope=Scope.REQUEST,
        provides=interfaces.ISecurity
    )

    get_guest_session_backend = provide(
        UserRepo,
        scope=Scope.REQUEST,
        provides=interfaces.IUser
    )


    get_okx_listner_config_interactor = provide(
        source=GetOkxListnerConfigsInteractor, 
        scope=Scope.REQUEST
    )

    save_okx_listner_config_interactor = provide(
        source=SaveOkxListnerConfigInteractor, 
        scope=Scope.REQUEST
    )

    signup_interactor = provide(
        source=SignupInteractor, 
        scope=Scope.REQUEST
    )

    login_interactor = provide(
        source=LoginInteractor, 
        scope=Scope.REQUEST
    )

    get_user_interactor = provide(
        source=GetUserInteractor, 
        scope=Scope.REQUEST
    )