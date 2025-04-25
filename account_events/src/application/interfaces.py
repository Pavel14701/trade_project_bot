from typing import Protocol
from abc import abstractmethod

from account_events.src.domain.entities import WebSocketDM


class IConnectionStorage(Protocol):
    @abstractmethod
    async def store_connection(self, config: WebSocketDM) -> None: ...

    @abstractmethod
    async def get_connection(self, user_id: int) -> WebSocketDM | None: ...

    @abstractmethod
    async def remove_connection(self, user_id: int) -> None: ...

    @abstractmethod
    async def get_active_connections(self) -> list[int]: ...


class IOkxAccountListner(Protocol):
    @abstractmethod
    async def connect(self, config: WebSocketDM) -> None: ...

    @abstractmethod
    async def update_subscriptions(self, config: WebSocketDM) -> None: ...

    @abstractmethod
    async def close_connection(self, config: WebSocketDM) -> None: ...


class IConfigEncryption(Protocol):
    @abstractmethod
    async def encrypt(self, model: WebSocketDM) -> WebSocketDM: ...

    @abstractmethod
    async def decrypt(self, model: WebSocketDM) -> WebSocketDM: ...