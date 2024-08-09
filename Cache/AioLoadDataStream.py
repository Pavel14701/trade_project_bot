#libs
import sys, pandas as pd

from Cache.AioRedisCache import AioRedisCache

sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from typing import Optional
#api
from Api.OKXInfoAsync import OKXInfoFunctionsAsync
#database
from DataSets.DataBaseAsync import DataAllDatasetsAsync
#utils
from DataSets.Utils.DataFrameUtilsAsync import create_dataframe_async, prepare_many_data_to_append_db_async
from Logs.CustomDecorators import log_exceptions_async
from Logs.CustomLogger import create_logger


logger = create_logger(logger_name = 'LoadDataStreamAsync')


class AioStreamData(OKXInfoFunctionsAsync, AioRedisCache):
    def __init__(
        self, instId:Optional[str]=None, timeframe:Optional[str]=None,
        lenghts:Optional[int]=None, load_data_after:Optional[str]=None,
        load_data_before:Optional[str]=None
        ):
        self.instId = instId
        self.timeframe = timeframe
        self.lenghts = lenghts
        OKXInfoFunctionsAsync.__init__(instId, timeframe, lenghts, load_data_after, load_data_before)
        AioRedisCache.__init__(
            self, instId=instId,
            channel = f'channel_{self.instId}_{self.timeframe}',
            timeframe=self.timeframe,
            key='postions'
        )


    @log_exceptions_async(logger)
    async def async_load_data(self) -> pd.DataFrame:
        result = await self.get_candlesticks_async(self.lenghts)
        prepare_df = await prepare_many_data_to_append_db_async(result)
        await DataAllDatasetsAsync(self.instId, self.timeframe).save_charts_async(prepare_df)
        data = await create_dataframe_async(prepare_df)
        await self.async_add_data_to_cache(data)
        return data


    @log_exceptions_async(logger)
    async def async_load_data_for_period(self, data:pd.DataFrame) -> pd.DataFrame:
        data = data.drop(data.index[:1])
        result = await self.get_candlesticks_async(lengths=1)
        prepare_df = await prepare_many_data_to_append_db_async(result)
        await DataAllDatasetsAsync(self.instId, self.timeframe).save_charts_async(prepare_df)
        new_data = await create_dataframe_async(prepare_df)
        return pd.concat([data, new_data], ignore_index=True)