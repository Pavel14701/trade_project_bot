from contextlib import asynccontextmanager
from typing import AsyncIterator

from argon2 import PasswordHasher
from dishka import make_async_container
from fastapi import FastAPI
from faststream.rabbit import RabbitBroker

from main_app.src.config import Config
from main_app.src.fastapi_app import create_fastapi_app
from main_app.src.faststream_app import create_faststream_app
from main_app.src.infrastructure.factories.rabbit import new_broker
from main_app.src.ioc import AppProvider

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
