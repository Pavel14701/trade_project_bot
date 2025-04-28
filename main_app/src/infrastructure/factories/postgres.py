from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from main_app.src.config import PostgresConfig


def new_session_maker(psql_config: PostgresConfig) -> async_sessionmaker[AsyncSession]:
    raw_url = "postgresql+psycopg://{login}:{password}@{host}:{port}/{database}"
    database_uri = raw_url.format(
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
    return async_sessionmaker(
        bind=engine, 
        class_=AsyncSession, 
        autoflush=False, 
        expire_on_commit=False
    )