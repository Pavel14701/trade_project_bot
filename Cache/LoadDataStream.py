#libs
import sys, pandas as pd
from typing import Optional
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
#Api
from Api.OKXInfo import OKXInfoFunctions
#database
from DataSets.DataBase import DataAllDatasets
#utils
from DataSets.Utils.DataFrameUtils import create_dataframe, prepare_many_data_to_append_db
from Logs.CustomDecorators import log_exceptions
from Logs.CustomLogger import create_logger


import pandas as pd
from pandas import DataFrame
logger = create_logger(logger_name = 'LoadStreamData')


class StreamData(OKXInfoFunctions):
    def __init__(
        self, instId:Optional[str]=None, timeframe:Optional[str]=None,
        lenghts:Optional[int]=None, load_data_after:Optional[str]=None,
        load_data_before:Optional[str]=None
        ):
        OKXInfoFunctions.__init__(self, instId, timeframe, lenghts, load_data_after, load_data_before)
        self.instId = instId
        self.timeframe = timeframe
        self.lenghts = lenghts


    @log_exceptions(logger)
    def load_data(self) -> pd.DataFrame:
        prepared_df = prepare_many_data_to_append_db(self.get_market_data(self.lenghts))
        DataAllDatasets(self.instId, self.timeframe).save_charts(prepared_df)
        return prepared_df


    @log_exceptions(logger)
    def load_data_for_period(self, data:pd.DataFrame) -> pd.DataFrame:
        data = data.drop(data.index[:1])
        prepare_df = prepare_many_data_to_append_db(self.get_market_data(lengths=1))
        DataAllDatasets(self.instId, self.timeframe).save_charts(prepare_df)
        df = pd.concat([data, create_dataframe(prepare_df)], ignore_index=True)
        print(df)
        return df
