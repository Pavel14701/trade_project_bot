import pickle, time, json, sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from redis import Redis
import pandas as pd
from User.LoadSettings import LoadUserSettingData


class RedisCache(LoadUserSettingData): 
    def __init__(self, instId:str, channel=None|str, timeframe=None|str, data=None|pd.DataFrame):
        super().__init__()
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
        try:
            pubsub = self.r.pubsub()
            pubsub.subscribe(self.channel)
            while True:
                message = pubsub.get_message()
                if message and message['type'] == 'message':
                    command = pickle.loads(message['data'])
                    print(command, type(command))
                    message_pickle = pickle.dumps(command)
                    self.r.set(f'message_{self.instId}_{self.timeframe}', message_pickle)
                time.sleep(1)
        except Exception as e:
            print(e)


    # Функция для публикации сообщения
    def publish_message(self, message):
        message_pickle = pickle.dumps(message)
        self.r.publish(self.channel, message_pickle)
        
        
    def load_message_from_cache(self):
        try:
            return pickle.loads(self.r.get(f'message_{self.instId}_{self.timeframe}'))
        except Exception as e:
            print(e)


from threading import Thread
a = RedisCache('asdas12312', 'fuck', 'fr', None)
print('class created')
def test():
    a.listen_to_redis_channel()
thread = Thread(target=test)
thread.start()
print('thread started')
list = {'asda': 'asda', 'dsasf': 'adsad', 'adsad': 'asdasdg'}
a.publish_message(list)
print('message published')
c = a.load_message_from_cache()
print(c)

