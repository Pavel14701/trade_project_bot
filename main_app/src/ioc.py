import base64
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
        key = config.secret.config_secret_key
        try:
            decoded_key = base64.urlsafe_b64decode(key)
        except Exception as e:
            raise ValueError("""
                Invalid Fernet encryption key: 
                is not a valid URL-safe 
                base64 string.
            """) from e
        if len(decoded_key) != 32:
            raise ValueError("""
                Invalid Fernet encryption key: 
                The decoded key must be 
                exactly 32 bytes.
            """)
        return Fernet(key)

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

    for name, (provider, interface) in {
        "cookie_repo": (
            CookieRepo, interfaces.ICookieBackend
        ),
        "error_handler_repo": (
            ExceptionHandlersRepo, interfaces.IErrorHandler
        ),
        "session_backend": (
            RedisSessionBackend, interfaces.ISessionBackend
        ),
        "guest_session_backend": (
            GuestSessionBackend, interfaces.IGuestSessionBackend
        ),
        "config_encryptor": (
            ConfigEncryptionRepo, interfaces.IConfigEncryption
        ),
        "security_repo": (
            SecurityRepo, interfaces.ISecurity
        ),
        "user_repo": (
            UserRepo, interfaces.IUser
        ),
    }.items():
        vars()[name] = provide(provider, scope=Scope.REQUEST, provides=interface)

    for name, interactor in {
        "get_okx_listener_config": GetOkxListnerConfigsInteractor,
        "save_okx_listener_config": SaveOkxListnerConfigInteractor,
        "signup": SignupInteractor,
        "login": LoginInteractor,
        "get_user": GetUserInteractor,
    }.items():
        vars()[name] = provide(source=interactor, scope=Scope.REQUEST)
