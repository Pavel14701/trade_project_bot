import pickle, sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from redis import Redis
import pandas as pd
from User.LoadSettings import LoadUserSettingData


class RedisCache(LoadUserSettingData): 
    def __init__(self, instId=None|str, channel=None|str, timeframe=None|str, key=None|str, data=None|pd.DataFrame):
        super().__init__()
        self.data = data
        self.instId = instId
        self.timeframe = timeframe
        self.channel = channel
        self.key = key
        self.r = Redis(self.host, self.port, self.db)


    def add_data_to_cache(self, data):
        pickled_df = pickle.dumps(data)
        self.r.set(f'df_{self.instId}_{self.timeframe}', pickled_df)


    def load_data_from_cache(self):
        data = pickle.loads(self.r.get(f'df_{self.instId}_{self.timeframe}'))
        return pd.DataFrame(data)
        
        
    #Настройка и подключение слушателя редис
    def subscribe_to_redis_channel(self):
        self.pubsub = self.r.pubsub()
        self.pubsub.subscribe(self.channel)
    
            
    def check_redis_message(self):
        message = self.pubsub.get_message()
        if message and message['type'] == 'message':
            self.command = pickle.loads(message['data'])
        return self.command
            
    
    def send_redis_command(self, message, key:str):
        message_pickle = pickle.dumps(message)
        self.r.set(key, message_pickle)


    # Функция для публикации сообщения
    def publish_message(self, message):
        message_pickle = pickle.dumps(message)
        self.r.publish(self.channel, message_pickle)
        
        
    def load_message_from_cache(self):
        try:
            return pickle.loads(self.r.get(self.key))
        except Exception as e:
            print(e)


    def set_state(self, orderId, instId:str, state:str):
        key = f'state_{instId}'
        state_pickle = pickle.dumps([state, instId, orderId])
        self.redis.set(key, state_pickle)


    def load_state(self):
        key = f'state_{self.instId}'
        return pickle.loads(self.r.get(key))