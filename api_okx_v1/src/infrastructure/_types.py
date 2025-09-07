from typing import TypeVar

from httpx import AsyncClient

from api_okx_v1.src.infrastructure.consts import OkxBaseConsts


class MarketClient(AsyncClient):
    pass


class PrivateClient(AsyncClient):
    pass


TClient = TypeVar("TClient", bound=AsyncClient)
TConsts = TypeVar("TConsts", bound=OkxBaseConsts)
