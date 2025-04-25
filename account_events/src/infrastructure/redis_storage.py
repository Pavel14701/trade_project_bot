from redis.asyncio import Redis
import json
from account_events.src.domain.entities import WebSocketDM

class ConnectionStorageGateway:
    def __init__(self, conn: Redis) -> None:
        self._conn = conn

    async def store_connection(self, config: WebSocketDM) -> None:
        """Сохраняет WebSocket-конфигурацию пользователя в Redis."""
        async with self._conn as conn:
            await conn.set(f"user_connection:{config.user_id}", json.dumps(config.to_dict()))

    async def get_connection(self, user_id: int) -> WebSocketDM | None:
        """Получает WebSocket-конфигурацию пользователя из Redis и преобразует в DTO."""
        async with self._conn as conn:
            config = await conn.get(f"user_connection:{user_id}")
        return WebSocketDM(**json.loads(config)) if config else None

    async def remove_connection(self, user_id: int) -> None:
        """Удаляет WebSocket-конфигурацию пользователя из Redis."""
        async with self._conn as conn:
            await conn.delete(f"user_connection:{user_id}")

    async def get_active_connections(self) -> list[int]:
        """Получает список всех активных подключений из Redis."""
        async with self._conn as conn:
            keys: list[bytes] = await conn.keys("user_connection:*")
        return [int(key.decode().split(":")[-1]) for key in keys]
