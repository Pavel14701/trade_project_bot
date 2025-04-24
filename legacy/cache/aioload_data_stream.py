#libs
import pandas as pd
from cache.aioredis_cache import AioRedisCache
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
#api
from api.okx_info_async import OKXInfoFunctionsAsync
#database
from datasets.database_async import DataAllDatasetsAsync
#utils
from datasets.utils.dataframe_utils_async import create_dataframe_async, prepare_many_data_to_append_db_async
from baselogs.custom_decorators import log_exceptions_async
from baselogs.custom_logger import create_logger


logger = create_logger(logger_name = 'LoadDataStreamAsync')


class AioStreamData(OKXInfoFunctionsAsync, AioRedisCache):
    def __init__(
        self,Session:AsyncSession, classes_dict:dict, instId:Optional[str]=None, timeframe:Optional[str]=None,
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
        self.Session = Session
        self.classes_dict = classes_dict


    @log_exceptions_async(logger)
    async def async_load_data(self) -> pd.DataFrame:
        result = await self.get_candlesticks(self.lenghts)
        prepare_df = await prepare_many_data_to_append_db_async(result)
        await DataAllDatasetsAsync(self.Session, self.classes_dict, self.instId, self.timeframe)\
            .save_charts_async(prepare_df)
        data = await create_dataframe_async(prepare_df)
        await self.async_add_data_to_cache(data)
        return data


    @log_exceptions_async(logger)
    async def async_load_data_for_period(self, data:pd.DataFrame) -> pd.DataFrame:
        data = data.drop(data.index[:1])
        result = await self.get_candlesticks(lengths=1)
        prepare_df = await prepare_many_data_to_append_db_async(result)
        await DataAllDatasetsAsync(self.Session, self.classes_dict, self.instId, self.timeframe)\
            .save_charts_async(prepare_df)
        new_data = await create_dataframe_async(prepare_df)
        return pd.concat([data, new_data], ignore_index=True)