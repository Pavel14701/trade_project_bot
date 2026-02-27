from redis.asyncio import Redis # type: ignore

from config import RedisConfig


async def new_redis_client(redis_config: RedisConfig) -> Redis:
    return Redis(
        host=redis_config.host,
        port=redis_config.port,
        db=redis_config.db,
        password=redis_config.password
    )