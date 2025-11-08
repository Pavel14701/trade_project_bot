"""
Defines reusable type aliases and client wrappers for HTTP communication 
  with the OKX API.

This module includes:
- `MarketClient`: A subclass of `httpx.AsyncClient` used for public market 
  data requests.
- `PrivateClient`: A subclass of `httpx.AsyncClient` used for authenticated 
  private account and trading requests.
- Type variables for generic programming across infrastructure layers.

These definitions are used throughout the application to enforce type 
  safety and distinguish between
public and private API clients.
"""


from typing import TypeVar

from httpx import AsyncClient

from api_okx_v1.src.infrastructure.consts import OkxBaseConsts


class MarketClient(AsyncClient):
    pass


class PrivateClient(AsyncClient):
    pass


TClient = TypeVar("TClient", bound=AsyncClient)
TConsts = TypeVar("TConsts", bound=OkxBaseConsts)
DataclassType = TypeVar("DataclassType")