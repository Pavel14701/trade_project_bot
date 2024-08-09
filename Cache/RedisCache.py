#libs
import pickle, sys, pandas as pd
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from typing import Optional
from redis import Redis
#configs
from Configs.LoadSettings import LoadUserSettingData
#utils
from Logs.CustomDecorators import log_exceptions
from Logs.CustomLogger import create_logger


logger = create_logger('RedisCache')


class RedisCache(Redis): 
    def __init__(
        self, instId:Optional[str]=None, timeframe:Optional[str]=None, channel:Optional[str]=None,
        key:Optional[str]=None, data:Optional[pd.DataFrame]=None
        ):
        db_settings = LoadUserSettingData().load_cache_settings()
        self.host = db_settings['host']
        self.port = db_settings['port']
        self.db = db_settings['db']
        Redis.__init__(self, host=self.host, port=self.port, db=self.db)
        user_settings = LoadUserSettingData().load_user_settings()
        self.timeframes = user_settings['timeframes']
        self.instIds = user_settings['instIds']
        self.data = data
        self.instId = instId
        self.timeframe = timeframe
        self.channel = channel
        self.key = key


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
        return pickle.loads(self.get(self.key))