# In Develop
import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
#settings
from configs.load_settings import ConfigsProvider
#datasets
from datasets.database_async import DataAllDatasetsAsync
from cache.aioload_data_stream import AioStreamData
from cache.aioredis_cache import AioRedisCache
from datasets.async_states_db import AsyncStateRequest
#indicators
from indicators.avsl_ind import AVSLIndicator
from indicators.adx_ind import ADXTrend
from indicators.rsi_clouds_ind import CloudsRsi
#utils
from datasets.utils.dataframe_utils import create_message_state_avsl_rsi_clouds
from datasets.utils.dataframe_utils_async import create_dataframe_async, prepare_many_data_to_append_db_async
from baselogs.custom_logger import create_logger
from baselogs.custom_decorators import log_exceptions_async
#logger
logger = create_logger('Signals')


class CheckActiveStateAsync(AioStreamData, AioRedisCache):
    def __init__(self, instId:str, timeframe:str, lenghtsSt:int, strategy:str):
        self.lenghtsSt = lenghtsSt
        self.instId = instId
        self.timeframe = timeframe
        self.strategy = strategy
        self.channel = f'channel_{self.instId}_{self.timeframe}'
        AioStreamData.__init__(self, self.instId, self.timeframe, self.lenghtsSt, None, None)
        AioRedisCache.__init__(self, self.instId, self.timeframe, self.channel, key='positions')


    @log_exceptions_async(logger)
    async def add_data_to_redis_async(self):
        result = await self.async_load_data()
        prepare_df = await prepare_many_data_to_append_db_async(result)
        await DataAllDatasetsAsync(self.instId, self.timeframe).save_charts_async(prepare_df)
        data = await create_dataframe_async(prepare_df)
        await self.async_add_data_to_cache(data)

    @log_exceptions_async(logger)
    async def check_active_state_async(self):
        try:
            positions = await self.async_load_message_from_cache()
            instIds_match_list = [i for i, val in enumerate(positions['instId']) if val == self.instId]
            async for index in instIds_match_list:
                if positions['timeframe'][index] == self.timeframe:
                    search_index = index
                    break
            return positions['state'][search_index]
        except ValueError:
            state_instance = AsyncStateRequest(self.instId, self.timeframe, self.strategy)
            if state_params := await state_instance.check_state_async():
                return state_params['state']
            await state_instance.save_none_state_async()
            return None


class AvslRsiCloudsStrategy(CheckActiveStateAsync):
    def __init__ (self, instId:str, timeframe:str, lenghtsSt:int):
        self.strategy = 'avsl_rsi_clouds'
        CheckActiveStateAsync.__init__(instId, timeframe, lenghtsSt, self.strategy)
        self.adx_trigger = ConfigsProvider.load_adx_configs()['adx_trigger']
        
        

    @log_exceptions_async(logger)
    async def create_signals(self) -> None:
        data = await self.async_load_data_from_cache()
        data = await self.async_load_data_for_period(data)
        avsl = await AVSLIndicator(data).calculate_avsl_async()
        rsi = await CloudsRsi(data).calculate_rsi_macd_async()
        adx = await ADXTrend(data).calculate_adx_async()
        message = create_message_state_avsl_rsi_clouds(self.instId, self.timeframe, avsl, adx, rsi)
        await self.async_add_data_to_cache(data)
        if rsi is not None and adx >= self.adx_trigger:
            await self.async_publish_message(message)

    @log_exceptions_async(logger)
    async def trailing_stoploss(self) -> None: #Базирован на индикаторе авсл
        data = await self.async_load_data_from_cache()
        data = await self.async_load_data_for_period(data)
        indicator_avsl = AVSLIndicator(data)
        avsl = indicator_avsl.calculate_avsl()
        message = create_message_state_avsl_rsi_clouds(self.instId, self.timeframe, avsl)
        await self.async_publish_message(self.channel, message)
