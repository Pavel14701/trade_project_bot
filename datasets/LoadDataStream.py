import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
import pandas as pd
from pandas import DataFrame
from sqlalchemy.orm import sessionmaker
from User.UserInfoFunctions import UserInfo
from datasets.database import DataAllDatasets




class StreamData(UserInfo):
    def __init__(
        self, Session=None|sessionmaker, classes_dict=None|dict, instId=None|str, timeframe=None|str,
        lenghts=None|int, load_data_after=None|str, load_data_before=None|str
        ):
        super().__init__(instId, timeframe, lenghts, load_data_after, load_data_before)
        self.instId = instId
        self.timeframe = timeframe
        self.lenghts = lenghts
        self.Session = Session
        self.classes_dict = classes_dict


        
    def load_data(self) -> dict:
        return super().get_market_data(self.lenghts)

    
    def load_data_for_period(self, data:DataFrame) -> pd.DataFrame:
        bd = DataAllDatasets(self.instId, self.timeframe, self.Session, self.classes_dict)
        data = data.drop(data.index[:1])
        new_data = super().get_market_data(lenghts=1)
        bd.save_charts(new_data)
        return pd.concat([data, new_data], ignore_index=True)
