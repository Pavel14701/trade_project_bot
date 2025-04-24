from argon2 import PasswordHasher
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from cryptography.fernet import Fernet

from main_app.src.config import PostgresConfig, AppConfig


def new_session_maker(psql_config: PostgresConfig) -> async_sessionmaker[AsyncSession]:
    database_uri = "postgresql+psycopg://{login}:{password}@{host}:{port}/{database}".format(
        login=psql_config.login,
        password=psql_config.password,
        host=psql_config.host,
        port=psql_config.port,
        database=psql_config.database,
    )

    engine = create_async_engine(
        database_uri,
        pool_size=15,
        max_overflow=15,
        connect_args={
            "connect_timeout": 5,
        },
    )
    return async_sessionmaker(engine, class_=AsyncSession, autoflush=False, expire_on_commit=False)


def get_cipher(app_config: AppConfig) -> Fernet:
    return Fernet(app_config.secret_key)

def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()
