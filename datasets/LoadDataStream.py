import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
import pandas as pd
from pandas import DataFrame
from User.UserInfoFunctions import UserInfo




class StreamData(UserInfo):
    def __init__(
        self, instId=None|str, timeframe=None|str,
        lenghts=None|int, load_data_after=None|str, load_data_before=None|str
        ):
        super().__init__(instId, timeframe, lenghts, load_data_after, load_data_before)
        self.instId = instId
        self.timeframe = timeframe
        self.lenghts = lenghts


        
    def load_data(self) -> dict:
        return super().get_market_data(self.lenghts)

    
    def load_data_for_period(self, data:DataFrame) -> pd.DataFrame:
        data = data.drop(data.index[:1])
        new_data = super().get_market_data(lenghts=1)
        df = pd.concat([data, new_data], ignore_index=True)
        print(df)
        return df
