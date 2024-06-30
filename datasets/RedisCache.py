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

"""
from threading import Thread
a = RedisCache('asdas12312', 'fuck', 'fr', None)
print('class created')
def test():
    a.subscribe_to_redis_channel()
    while True:
        with contextlib.suppress(Exception):
            a.check_redis_message()
            a.send_redis_command()
            time.sleep(1)
thread = Thread(target=test)
thread.start()
print('thread started')
list = {'asda': 'asda', 'dsasf': 'adsad', 'adsad': 'asdasdg'}
a.publish_message(list)
print('message published')
c = a.load_message_from_cache()
print(c)
"""