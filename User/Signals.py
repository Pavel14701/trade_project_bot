import sys, logging
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from User.LoadSettings import LoadUserSettingData
from datasets.database import DataAllDatasets, Session, classes_dict
from datasets.LoadDataStream import StreamData
from datasets.StatesDB import StateRequest
from indicators.AVSL import AVSLIndicator
from indicators.ADX import ADXTrend
from indicators.RsiClouds import CloudsRsi
from datasets.RedisCache import RedisCache
from utils.DataFrameUtils import create_dataframe, create_message_state_avsl_rsi_clouds, prepare_many_data_to_append_db


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('signals.log')
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class CheckActiveState(LoadUserSettingData):
    def __init__(self, instId:str, timeframe:str, lenghtsSt:int, strategy):
        super().__init__()
        self.lenghtsSt = lenghtsSt
        self.instId = instId
        self.timeframe = timeframe
        self.strategy = strategy
        self.channel = f'channel_{self.instId}_{self.timeframe}'
    
    def add_data_to_redis(self):
        result = StreamData(self.instId, self.timeframe, self.lenghtsSt, None, None).load_data()
        DataAllDatasets(self.instId, self.timeframe).save_charts(result)
        prepare_df = prepare_many_data_to_append_db(result)
        data = create_dataframe(prepare_df)
        RedisCache(self.instId, self.timeframe, self.channel, key='positions', data=data).add_data_to_cache(data)


    def check_active_state(self):
        try:
            positions = self.redis_func.load_message_from_cache()
            instIds_match_list = [i for i, val in enumerate(positions['instId']) if val == self.instId]
            for index in instIds_match_list:
                element_b = positions['timeframe'][index]
                is_match = element_b == self.timeframe
                if is_match:
                    search_index = index
                    break
            return positions['state'][search_index]
        except Exception:
            state_instance = StateRequest(self.Session, self.instId, self.timeframe, self.strategy)
            if state_params := state_instance.check_state():
                return state_params['state']
            state_instance.save_none_state()
            return None


class AVSL_RSI_ClOUDS(CheckActiveState):
    def __init__ (self, instId:str, timeframe:str, lenghtsSt:int):
        super().__init__(instId, timeframe, lenghtsSt, self.strategy)
        self.strategy = 'avsl_rsi_clouds'
        self.adx_trigger = 20
        


    def create_signals(self) -> None:
        #try:
            data = self.redis_func.load_data_from_cache()
            data = self.init.load_data_for_period(data)
            indicator_avsl = AVSLIndicator(data)
            indicator_rsi_clouds = CloudsRsi(data)
            indicator_adx = ADXTrend(data)
            avsl = indicator_avsl.calculate_avsl()
            rsi = indicator_rsi_clouds.calculate_rsi_clouds()
            adx = indicator_adx.calculate_adx()
            message = create_message_state_avsl_rsi_clouds(self.instId, self.timeframe, avsl, adx, rsi)
            self.redis_func.add_data_to_cache(data)
            if rsi is not None and adx >= self.adx_trigger:
                self.redis_func.publish_message(message)
        #except Exception as e:
            #logger.error(f"\n{datetime.now().isoformat()} Error create signals:\n{e}")


    def trailing_stoploss(self) -> None: #Базирован на индикаторе авсл
        try:
            data = self.redis_func.load_data_from_cache()
            data = self.init.load_data_for_period(data)
            bd = DataAllDatasets(self.instId, self.timeframe)
            bd.save_charts(data)
            indicator_avsl = AVSLIndicator(data)
            avsl = indicator_avsl.calculate_avsl()
            message = create_message_state_avsl_rsi_clouds(self.instId, self.timeframe, avsl)
            self.redis_func.publish_message(self.channel, message)
        except Exception as e:
            logger.error(f"\n{datetime.now().isoformat()} Error trailing stoploss:\n{e}")
