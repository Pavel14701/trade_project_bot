#libs
import pickle, pandas as pd
from typing import Optional
from redis import Redis
#configs
from configs.load_settings import ConfigsProvider
#utils
from baselogs.custom_decorators import log_exceptions
from baselogs.custom_logger import create_logger


logger = create_logger('RedisCache')


class RedisCache(Redis): 
    def __init__(
        self, instId:Optional[str]=None, timeframe:Optional[str]=None, channel:Optional[str]=None,
        key:Optional[str]=None, data:Optional[pd.DataFrame]=None
        ):
        db_settings = ConfigsProvider().load_cache_configs()
        self.host, self.port, self.db = db_settings['host'], db_settings['port'], db_settings['db']
        user_settings = ConfigsProvider().load_user_configs()
        self.timeframes, self.instIds = user_settings['timeframes'], user_settings['instIds']
        self.data, self.instId, self.timeframe, self.channel, self.key = data, instId, timeframe, channel, key
        Redis.__init__(self, host=self.host, port=self.port, db=self.db)


    @log_exceptions(logger)
    def add_data_to_cache(self, data:pd.DataFrame) -> None:
        self.set(f'df_{self.instId}_{self.timeframe}', pickle.dumps(data))


    @log_exceptions(logger)
    def load_data_from_cache(self) -> pd.DataFrame:
        data = pickle.loads(self.get(f'df_{self.instId}_{self.timeframe}'))
        return pd.DataFrame(data)


    @log_exceptions(logger)
    def subscribe_to_redis_channel(self) -> None:
        self.pubsub().subscribe(str(self.channel))


    @log_exceptions(logger)
    def subscribe_to_redis_channels(self):
        for instId in self.instIds:
            for timeframe in self.timeframes:
                channel = f'channel_{instId}_{timeframe}'
                self.pubsub().subscribe(channel)
                logger.info(f'Create redis listner from channel: {channel}')


    @log_exceptions(logger)
    def check_redis_message(self) -> dict:
        message = self.pubsub().get_message()
        if message and message['type'] == 'message':
            return pickle.loads(message['data'])


    @log_exceptions(logger)
    def send_redis_command(self, message:str, key:str) -> None:
        self.set(key, pickle.dumps(message))


    @log_exceptions(logger)
    def publish_message(self, message:str) -> None:
        self.publish(self.channel, pickle.dumps(message))


    @log_exceptions(logger)
    def load_message_from_cache(self) -> dict:
        if value := self.get(self.key) is not None:
            return pickle.loads(value)
        return None
        