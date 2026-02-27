from contextlib import asynccontextmanager
from typing import AsyncIterator

from argon2 import PasswordHasher # type: ignore
from dishka import make_async_container # type: ignore
from fastapi import FastAPI # type: ignore
from faststream.rabbit import RabbitBroker # type: ignore

from config import Config
from fastapi_app import create_fastapi_app
from faststream_app import create_faststream_app
from infrastructure.factories.rabbit import new_broker
from ioc import AppProvider

config = Config()
broker = new_broker(config.rabbitmq)
password_hasher = PasswordHasher()
container = make_async_container(
    AppProvider(),
    context={
        Config: config, 
        RabbitBroker: broker,
        PasswordHasher: password_hasher
    }
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    faststream_app = create_faststream_app(container, broker)
    if faststream_app.broker:
        await faststream_app.broker.start()
    yield
    if faststream_app.broker:
        await faststream_app.broker.close()


async def main() -> FastAPI:
    return await create_fastapi_app(container, lifespan)
