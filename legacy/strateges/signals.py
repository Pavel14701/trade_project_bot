#libs
from typing import Optional, Any
from datetime import datetime
#configs
from configs.load_settings import ConfigsProvider
#database
from datasets.states_db import StateRequest
#cache
from cache.redis_cache import RedisCache
from cache.load_data_stream import StreamData
#functions
from indicators.avsl_ind import AVSLIndicator
from indicators.adx_ind import ADXTrend
from indicators.rsi_clouds_ind import CloudsRsi
#utils
from baselogs.custom_logger import create_logger
from baselogs.custom_decorators import log_exceptions


logger = create_logger('Signals')


class CheckActiveState(StreamData, RedisCache):
    def __init__(self, instId:str, timeframe:str, lenghtsSt:int, strategy:str) -> None:
        self.lenghtsSt, self.instId, self.timeframe, self.strategy  = lenghtsSt, instId, timeframe, strategy
        self.channel = f'channel_{self.instId}_{self.timeframe}'
        self.key = 'positions'
        StreamData.__init__(self, self.instId, self.timeframe, self.lenghtsSt, None, None, self.channel, self.key)
        self.load_data()
        
    
    def __find_position_data(self) -> Any:
        if positions := self.load_message_from_cache():
            instIds_match_list = [i for i, val in enumerate(positions['instId']) if val == self.instId]
            for index in instIds_match_list:
                element_b = positions['timeframe'][index]
                is_match = element_b == self.timeframe
                if is_match:
                    search_index = index
                    break
            return positions['state'][search_index]
        return None


    def check_active_state(self) -> Optional[dict]:
        if state := self.__find_position_data():
            return state
        state_instance = StateRequest(self.instId, self.timeframe, self.strategy)
        if state := state_instance.check_state():
            return state
        state_instance.save_none_state()
        return None



class AVSL_RSI_ClOUDS(CheckActiveState):
    def __init__ (self, instId:str, timeframe:str, lenghtsSt:int) -> None:
        self.strategy = 'avsl_rsi_clouds'
        CheckActiveState.__init__(self, instId, timeframe, lenghtsSt, self.strategy)
        self.adx_trigger = ConfigsProvider.load_adx_configs()['adx_trigger']


    def __create_signal_message(self) -> dict:
        return dict([
            ('time', datetime.now().isoformat()),
            ('instId', self.instId),
            ('timeframe', self.timeframe),
            ('strategy', self.strategy),
            ('trend_strenghts', self.adx),
            ('signal', self.rsi_clouds),
            ('slPrice', self.avsl)
        ])


    @log_exceptions(logger)
    def create_signals(self) -> None:
            data = self.load_data_from_cache()
            data = self.load_data_for_period(data)
            self.avsl = AVSLIndicator(data).calculate_avsl()
            self.rsi_clouds = CloudsRsi(data).calculate_rsi_macd()
            self.adx = ADXTrend(data)._calculate_adx_sync()
            print(f'{self.avsl}\n{self.rsi_clouds}\n{self.adx}')
            message = self.__create_signal_message()
            self.add_data_to_cache(data)
            if self.rsi_clouds is not None and self.adx >= self.adx_trigger:
                self.publish_message(message)


    @log_exceptions(logger)
    def trailing_stoploss(self) -> None: #Базирован на индикаторе авсл
        data = self.load_data_from_cache()
        data = self.load_data_for_period(data)
        self.avsl = AVSLIndicator(data).calculate_avsl()
        self.adx, self.rsi_clouds = None
        message = self.__create_signal_message()
        self.publish_message(self.channel, message)
