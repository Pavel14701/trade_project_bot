from typing import Any, AsyncContextManager, Callable, Mapping

from dishka import AsyncContainer # type: ignore
from dishka.integrations import fastapi as fastapi_integration # type: ignore
from fastapi import FastAPI # type: ignore
from starlette.middleware import Middleware # type: ignore

from controllers.routes import router
from infrastructure.middlewares import SessionMiddleware
from infrastructure.repositories.sessions import (
    GuestSessionBackend,
    RedisSessionBackend,
)


async def create_fastapi_app(
    container: AsyncContainer, 
    lifespan: Callable[
        [FastAPI], AsyncContextManager[None]
    ] | Callable[
        [FastAPI], AsyncContextManager[Mapping[str, Any]]
    ] | None
) -> FastAPI:
    async with container() as opened:
        redis_backend = await opened.get(RedisSessionBackend)
        guest_backend = await opened.get(GuestSessionBackend)

        middleware = [
            Middleware(
                SessionMiddleware,
                redis_manager=redis_backend,
                guest_manager=guest_backend
            )
        ]

        fastapi_app = FastAPI(lifespan=lifespan, middleware=middleware)
        fastapi_app.include_router(router)
        fastapi_integration.setup_dishka(container=container, app=fastapi_app)

    return fastapi_app
