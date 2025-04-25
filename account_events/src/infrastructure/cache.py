from redis.asyncio import Redis
from account_events.src.config import RedisConfig

async def new_redis_client(redis_config: RedisConfig) -> Redis:
    return Redis(
        host=redis_config.host,
        port=redis_config.port,
        db=redis_config.db,
        password=redis_config.password
    )