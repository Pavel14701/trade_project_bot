import pickle, time, json, sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from redis import Redis
import pandas as pd
from User.LoadSettings import LoadUserSettingData


class RedisCache(LoadUserSettingData): 
    def __init__(self, instId:str, timeframe:str, channel:str, data=None|pd.DataFrame):
        super().__init__(self.host, self.port, self.db)
        self.data = data
        self.instId = instId
        self.timeframe = timeframe
        self.channel = channel
        self.r = Redis(self.host, self.port, self.db)
        
        
    def add_data_to_cache(self, data):
        pickled_df = pickle.dumps(data)
        self.r.set(f'df_{self.instId}_{self.timeframe}', pickled_df)


    def load_data_from_cache(self):
        data = pickle.loads(self.r.get(f'df_{self.instId}_{self.timeframe}'))
        return pd.DataFrame(data)
        
        
    #Настройка и подключение слушателя редис
    def listen_to_redis_channel(self):
        pubsub = self.r.pubsub()
        pubsub.subscribe('my-channel')
        while True:
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                print(f"Получено сообщение: {message['data'].decode('utf-8')}")
            time.sleep(1)


    # Функция для публикации сообщения
    def publish_message(self, channel, message):
        message_json = json.dumps(message)
        self.r.publish(channel, message_json)
        print(message_json)