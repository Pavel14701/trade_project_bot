from contextlib import asynccontextmanager

from argon2 import PasswordHasher
from dishka import make_async_container
from dishka.integrations import faststream as faststream_integration 
from dishka.integrations import fastapi as fastapi_integration
from fastapi import FastAPI
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from main_app.src.controllers.routes import router
from main_app.src.config import Config
from main_app.src.controllers.amqp import controller
from main_app.src.infrastructure.factories.rabbit import new_broker
from main_app.src.infrastructure.middlewares import SessionMiddleware
from main_app.src.infrastructure.repositories.sessions import (
    RedisSessionBackend,
    GuestSessionBackend
)
from main_app.src.ioc import AppProvider


config = Config()
broker = new_broker(config)
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
async def lifespan():
    faststream_app = get_faststream_app()
    await faststream_app.broker.start()
    yield
    await faststream_app.broker.close()

def get_faststream_app() -> FastStream: 
    faststream_app = FastStream(broker)
    faststream_integration.setup_dishka(
        container=container, 
        app=faststream_app, 
        auto_inject=True
    )
    broker.include_router(controller)
    return faststream_app


async def get_fastapi_app() -> FastAPI:
    fastapi_app = FastAPI(lifespan=lifespan)
    async with container() as opened:
        redis_backend = await opened.get(RedisSessionBackend)
        guest_backend = await opened.get(GuestSessionBackend)
    fastapi_app.include_router(router)
    fastapi_app.add_middleware(
        SessionMiddleware(
            app=fastapi_app,
            redis_manager=redis_backend,
            guest_manager=guest_backend  
        )
    )
    fastapi_integration.setup_dishka(
        container=container, 
        app=fastapi_app, 
    )
    return fastapi_app
