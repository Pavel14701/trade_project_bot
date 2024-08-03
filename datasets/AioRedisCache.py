import pickle, logging
from typing import Optional
from redis import asyncio as aioredis
from pandas import DataFrame
from datetime import datetime
from User.LoadSettings import LoadUserSettingData


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('listner.log')
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class AioRedisCache:
    def __init__(
        self, instId:Optional[str]=None, channel:Optional[str]=None, timeframe:Optional[str]=None,
        key:Optional[str]=None, data:Optional[DataFrame]=None
        ):
        cache_settings = LoadUserSettingData.load_cache_settings()
        self.host = cache_settings['host']
        self.port = cache_settings['port']
        self.db = cache_settings['db']
        self.data = data
        self.instId = instId
        self.timeframe = timeframe
        self.channel = channel
        self.key = key
        self.redis = None
        user_settings = LoadUserSettingData.load_user_settings()
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
            print(f"Error: {exc_type} - {exc_value}")
            print("Traceback:")
            await traceback.print_tb(traceback)
        await self.redis.aclose()


    async def async_add_data_to_cache(self, data:Optional[DataFrame]) -> None:
        pickled_df = pickle.dumps(data)
        await self.redis.set(f'df_{self.instId}_{self.timeframe}', pickled_df)


    async def async_load_data_from_cache(self) -> DataFrame:
        pickled_data = await self.redis.get(f'df_{self.instId}_{self.timeframe}')
        if pickled_data:
            data = pickle.loads(pickled_data)
            return DataFrame(data)


    async def async_subscribe_to_redis_channel(self) -> None:
        sub = self.redis.pubsub()
        await sub.subscribe(str(self.channel))


    async def async_subscribe_to_redis_channels(self):
        sub = self.redis.pubsub()
        for instId in self.instIds:
            for timeframe in self.timeframes:
                await sub.subscribe(f'channel_{instId}_{timeframe}')
                logger.info(
                    f'\n{datetime.now().isoformat()}: Created redis listener for channel: channel_{instId}_{timeframe}'
                )


    async def async_load_message_from_cache(self) -> dict:
        message = await self.redis.get(self.key)
        return pickle.loads(message) if message else None


    async def async_check_redis_message(self) -> dict:
        sub = self.redis.pubsub()
        await sub.subscribe(self.channel)
        async for message in sub.listen():
            if message['type'] == 'message':
                return pickle.loads(message['data'])


    async def async_send_redis_command(self, message:Optional[dict], key:str) -> None:
        message_pickle = pickle.dumps(message)
        await self.redis.set(key, message_pickle)


    async def async_publish_message(self, message: str) -> None:
        message_pickle = pickle.dumps(message)
        await self.redis.publish(self.channel, message_pickle)


    async def async_set_state(self, orderId, instId:str, state:str) -> None:
        key = f'state_{instId}'
        state_pickle = pickle.dumps([state, instId, orderId])
        await self.redis.set(key, state_pickle)
