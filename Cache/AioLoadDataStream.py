import sys, pandas as pd
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from typing import Optional
from pandas import DataFrame
from utils.DataFrameUtilsAsync import create_dataframe_async, prepare_many_data_to_append_db_async
from datasets.DataBaseAsync import DataAllDatasetsAsync
from User.UserInfoFunctionsAsync import UserInfoAsync
from utils.CustomLogger import create_logger
from utils.CustomDecorators import log_exceptions_async
logger = create_logger(logger_name = 'LoadStreamDataAsync')


class AioStreamData(UserInfoAsync):
    def __init__(
        self, instId:Optional[str]=None, timeframe:Optional[str]=None,
        lenghts:Optional[int]=None, load_data_after:Optional[str]=None,
        load_data_before:Optional[str]=None
        ):
        UserInfoAsync.__init__(instId, timeframe, lenghts, load_data_after, load_data_before)
        self.instId = instId
        self.timeframe = timeframe
        self.lenghts = lenghts


    @log_exceptions_async(logger)
    async def async_load_data(self) -> dict:
        return await self.get_candlesticks_async(self.lenghts)


    @log_exceptions_async(logger)
    async def async_load_data_for_period(self, data:DataFrame) -> pd.DataFrame:
        data = data.drop(data.index[:1])
        result = await self.get_candlesticks_async(lengths=1)
        prepare_df = await prepare_many_data_to_append_db_async(result)
        await DataAllDatasetsAsync(self.instId, self.timeframe).save_charts_async(prepare_df)
        new_data = await create_dataframe_async(prepare_df)
        return pd.concat([data, new_data], ignore_index=True)