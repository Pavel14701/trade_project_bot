import pickle, sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from redis import asyncio as aioredis
from pandas import DataFrame
from User.LoadSettings import LoadUserSettingData


class AioRedisCache(LoadUserSettingData):
    def __init__(self, instId=None|str, channel=None|str, timeframe=None|str, key=None|str, data=None|DataFrame):
        super().__init__()
        self.data = data
        self.instId = instId
        self.timeframe = timeframe
        self.channel = channel
        self.key = key
        self.redis = None


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


    async def async_load_message_from_cache(self) -> dict:
        message = await self.redis.get(self.key)
        return pickle.loads(message) if message else None


    async def async_send_redis_command(self, message:dict, key:str) -> None:
        message_pickle = pickle.dumps(message)
        await self.redis.set(key, message_pickle)


    async def async_set_state(self, orderId, instId:str, state:str) -> None:
        key = f'state_{instId}'
        state_pickle = pickle.dumps([state, instId, orderId])
        await self.redis.set(key, state_pickle)
