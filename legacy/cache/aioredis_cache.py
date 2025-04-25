#libs
import pickle
from typing import Optional
from redis import asyncio as aioredis
from pandas import DataFrame
from datetime import datetime
#configs
from configs.load_settings import ConfigsProvider
#utils
from baselogs.custom_logger import create_logger
from baselogs.custom_decorators import log_exceptions_async


logger = create_logger('AioRedisCache')


class AioRedisCache:
    def __init__(
        self, instId:Optional[str]=None, channel:Optional[str]=None, timeframe:Optional[str]=None,
        key:Optional[str]=None, data:Optional[DataFrame]=None
        ) -> None:
        cache_settings = ConfigsProvider().load_cache_configs()
        self.host = cache_settings['host']
        self.port = cache_settings['port']
        self.db = cache_settings['db']
        self.data = data
        self.instId = instId
        self.timeframe = timeframe
        self.channel = channel
        self.key = key
        self.redis = None
        user_settings = ConfigsProvider().load_user_configs()
        self.instIds = user_settings['instIds']
        self.timeframes = user_settings['timeframes']


    async def async_connect(self):
        self.redis = aioredis.Redis(
            host=self.host,
            port=self.port,
            db=self.db
        )


    async def __aenter__(self):
        await self.async_connect()
        return self


    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type:
            error_message = (
                f"Error: {exc_type} - {exc_value}\n"
                "Traceback:\n"
                ''.join(traceback.format_tb(traceback))
            )
            logger.error(error_message)
        await self.redis.aclose()


    @log_exceptions_async(logger)
    async def async_add_data_to_cache(self, data:Optional[DataFrame]) -> None:
        await self.redis.set(f'df_{self.instId}_{self.timeframe}', pickle.dumps(data))


    @log_exceptions_async(logger)
    async def async_load_data_from_cache(self) -> DataFrame:
        pickled_data = await self.redis.get(f'df_{self.instId}_{self.timeframe}')
        if pickled_data:
            return DataFrame(pickle.loads(pickled_data))


    @log_exceptions_async(logger)
    async def async_subscribe_to_redis_channel(self) -> None:
        await self.redis.pubsub().subscribe(str(self.channel))


    @log_exceptions_async(logger)
    async def async_subscribe_to_redis_channels(self) -> None:
        for instId in self.instIds:
            for timeframe in self.timeframes:
                await self.redis.pubsub().subscribe(f'channel_{instId}_{timeframe}')
                logger.info(
                    f'\n{datetime.now().isoformat()}: Created redis listener for channel: channel_{instId}_{timeframe}'
                )


    @log_exceptions_async(logger)
    async def async_load_message_from_cache(self) -> dict:
        message = await self.redis.get(self.key)
        return pickle.loads(message) if message else None


    @log_exceptions_async(logger)
    async def async_check_redis_message(self) -> dict:
        await self.redis.pubsub().subscribe(self.channel)
        async for message in self.redis.pubsub().listen():
            if message['type'] == 'message':
                return pickle.loads(message['data'])


    @log_exceptions_async(logger)
    async def async_send_redis_command(self, message:Optional[dict], key:str) -> None:
        await self.redis.set(key, pickle.dumps(message))


    @log_exceptions_async(logger)
    async def async_publish_message(self, message: str) -> None:
        await self.redis.publish(self.channel, pickle.dumps(message))


    @log_exceptions_async(logger)
    async def async_set_state(self, orderId:str, instId:str, state:str) -> None:
        await self.redis.set(f'state_{instId}', pickle.dumps([state, instId, orderId]))
