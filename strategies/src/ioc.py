from typing import AsyncIterable

from dishka import Provider, Scope, provide  # type: ignore
from httpx import AsyncClient


class MainAppProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, 
    ) -> AsyncIterable[AsyncClient]:
        async with AsyncClient(http2=True) as session:
            yield session
