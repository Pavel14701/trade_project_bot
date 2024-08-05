import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from typing import Optional
import pandas as pd
from pandas import DataFrame
from utils.DataFrameUtils import create_dataframe, prepare_many_data_to_append_db
from datasets.DataBase import DataAllDatasets
from User.UserInfoFunctions import UserInfo
from utils.CustomLogger import create_logger
from utils.CustomDecorators import log_exceptions


logger = create_logger(logger_name = 'LoadStreamData')


class StreamData(UserInfo):
    def __init__(
        self, instId:Optional[str]=None, timeframe:Optional[str]=None,
        lenghts:Optional[int]=None, load_data_after:Optional[str]=None,
        load_data_before:Optional[str]=None
        ):
        super().__init__(instId, timeframe, lenghts, load_data_after, load_data_before)
        self.instId = instId
        self.timeframe = timeframe
        self.lenghts = lenghts


    @log_exceptions(logger)
    def load_data(self) -> dict:
        return super().get_market_data(self.lenghts)


    @log_exceptions(logger)
    def load_data_for_period(self, data:DataFrame) -> pd.DataFrame:
        data = data.drop(data.index[:1])
        result = super().get_market_data(lengths=1)
        prepare_df = prepare_many_data_to_append_db(result)
        DataAllDatasets(self.instId, self.timeframe).save_charts(prepare_df)
        new_data = create_dataframe(prepare_df)
        df = pd.concat([data, new_data], ignore_index=True)
        print(df)
        return df
