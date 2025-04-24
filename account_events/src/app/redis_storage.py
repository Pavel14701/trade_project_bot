from redis.asyncio import Redis
import json

redis_client = Redis(host="localhost", port=6379, db=0)

async def store_connection(user_id: int, config: dict):
    """Сохраняет WebSocket-конфигурацию пользователя в Redis"""
    await redis_client.set(f"user_connection:{user_id}", json.dumps(config))

async def get_connection(user_id: int) -> dict:
    """Получает WebSocket-конфигурацию пользователя из Redis"""
    config = await redis_client.get(f"user_connection:{user_id}")
    return json.loads(config) if config else None

async def remove_connection(user_id: int):
    """Удаляет WebSocket-конфигурацию пользователя из Redis"""
    await redis_client.delete(f"user_connection:{user_id}")
