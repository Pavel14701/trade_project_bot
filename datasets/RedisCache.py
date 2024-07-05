import pickle, sys, logging
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from datetime import datetime
from redis import Redis
import pandas as pd
from User.LoadSettings import LoadUserSettingData


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('listner.log')
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class RedisCache(LoadUserSettingData): 
    def __init__(self, instId=None|str, channel=None|str, timeframe=None|str, key=None|str, data=None|pd.DataFrame):
        super().__init__()
        self.data = data
        self.instId = instId
        self.timeframe = timeframe
        self.channel = channel
        self.key = key
        self.r = Redis(self.host, self.port, self.db)


    def add_data_to_cache(self, data) -> None:
        pickled_df = pickle.dumps(data)
        self.r.set(f'df_{self.instId}_{self.timeframe}', pickled_df)


    def load_data_from_cache(self) -> pd.DataFrame:
        data = pickle.loads(self.r.get(f'df_{self.instId}_{self.timeframe}'))
        return pd.DataFrame(data)


    #Настройка и подключение слушателя редис
    def subscribe_to_redis_channel(self) -> None:
        self.pubsub = self.r.pubsub()
        self.pubsub.subscribe(str(self.channel))


    def subscribe_to_redis_channels(self):
        self.pubsub = self.r.pubsub()
        for instId in self.instIds:
            for timeframe in self.timeframes:
                chn = f'channel_{instId}_{timeframe}'
                self.pubsub.subscribe(chn)
                logger.info(f'\n{datetime.now().isoformat()}: Create redis listner from channel: {chn}')

    def check_redis_message(self) -> dict:
        message = self.pubsub.get_message()
        if message and message['type'] == 'message':
            self.command = pickle.loads(message['data'])
        return self.command


    def send_redis_command(self, message, key:str) -> None:
        message_pickle = pickle.dumps(message)
        self.r.set(key, message_pickle)


    # Функция для публикации сообщения
    def publish_message(self, message) -> None:
        message_pickle = pickle.dumps(message)
        self.r.publish(self.channel, message_pickle)


    def load_message_from_cache(self) -> dict:
        return pickle.loads(self.r.get(self.key))



    def set_state(self, orderId, instId:str, state:str) -> None:
        key = f'state_{instId}'
        state_pickle = pickle.dumps([state, instId, orderId])
        self.redis.set(key, state_pickle)


    def load_state(self) -> dict:
        key = f'state_{self.instId}'
        return pickle.loads(self.r.get(key))