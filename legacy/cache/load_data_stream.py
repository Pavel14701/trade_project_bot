#libs
import pandas as pd
from typing import Optional
from sqlalchemy.orm import sessionmaker
#Api
from api.okx_info import OKXInfoFunctions
#database
from datasets.database import DataAllDatasets
#cache
from cache.redis_cache import RedisCache
#utils
from datasets.utils.dataframe_utils import create_dataframe, prepare_many_data_to_append_db
from baselogs.custom_decorators import log_exceptions
from baselogs.custom_logger import create_logger


logger = create_logger(logger_name = 'LoadStreamData')


class StreamData(OKXInfoFunctions):
    def __init__(
        self, Session:sessionmaker, classes_dict:dict, instId:Optional[str]=None, timeframe:Optional[str]=None,
        lenghts:Optional[int]=None, load_data_after:Optional[str]=None,
        load_data_before:Optional[str]=None, channel:Optional[str]=None,
        key:Optional[str]=None
        ):
        OKXInfoFunctions.__init__(self, instId, timeframe, lenghts, load_data_after, load_data_before)
        self.key = key
        self.instId = instId
        self.timeframe = timeframe
        self.lenghts = lenghts
        self.channel = channel
        RedisCache.__init__(self, self.instId, self.timeframe, self.channel, self.key)
        self.Session = Session
        self.classes_dict = classes_dict


    @log_exceptions(logger)
    def load_data(self) -> pd.DataFrame:
        prepared_df = prepare_many_data_to_append_db(self.get_market_data(self.lenghts))
        DataAllDatasets(self.Session, self.classes_dict, self.instId, self.timeframe)\
            .save_charts(prepared_df)
        self.add_data_to_cache(create_dataframe(prepared_df))


    @log_exceptions(logger)
    def load_data_for_period(self, data:pd.DataFrame) -> pd.DataFrame:
        data = data.drop(data.index[:1])
        prepare_df = prepare_many_data_to_append_db(self.get_market_data(lengths=1))
        DataAllDatasets(self.Session, self.classes_dict, self.instId, self.timeframe)\
            .save_charts(prepare_df)
        df = pd.concat([data, create_dataframe(prepare_df)], ignore_index=True)
        print(df)
        return df
