import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from datetime import datetime
import pandas as pd
from indicators.AVSL import AVSLIndicator
from datasets.RedisCache import RedisCache
from LoadSettings import LoadUserSettingData
from datasets.LoadDataStream import StreamData

# Супер залупер класс
class CheckSignalData(LoadUserSettingData):
    def __init__ (self, Session, classes_dict, instId:str, timeframe:str, lenghtsSt:int, channel:str):
        super().__init__()
        self.lenghtsSt = lenghtsSt
        self.instId = instId
        self.timeframe = timeframe
        self.Session = Session
        self.classes_dict = classes_dict
        self.channel = channel
        self.init = StreamData(self.Session, self.classes_dict, self.instId, self.timeframe, self.lenghtsSt)
        data = self.init.load_data()
        self.redis_func = RedisCache(self.instId, self.timeframe, self.channel, self.data)
        self.redis_func.add_data_to_cache(data)
        


        
    def avsl_signals(self):
        try:
            data = self.redis_func.load_data_from_cache()
            data = self.init.load_data_for_period(data)
            indicator = AVSLIndicator(data)
            cross_up, cross_down, AVSL, close_prices, last_bar_signal = indicator.calculate_avsl()
            current_time = datetime.now()
            formatted_time = current_time.isoformat()
            message = dict([
                ("time", formatted_time),
                ("instId", self.instId),
                ("timeframe", self.timeframe),
                ("signal", last_bar_signal)
            ])
            self.redis_func.add_data_to_cache(data)
            self.redis_func.publish_message(message)
        except Exception as e:
            print(f'\nПроизошла ошибка: \n{e}\n')
        
        
        
        
        
        