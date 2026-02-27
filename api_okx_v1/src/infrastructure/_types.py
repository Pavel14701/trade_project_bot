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

from httpx import AsyncClient # type: ignore


class MarketClient(AsyncClient):
    pass


class PrivateClient(AsyncClient):
    pass


DataclassType = TypeVar("DataclassType")