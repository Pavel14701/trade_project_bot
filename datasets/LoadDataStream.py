import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from datasets.database import DataAllDatasets, Base
import pandas as pd
from User.LoadSettings import LoadUserSettingData


class StreamData(LoadUserSettingData):
    def __init__(self, Session, classes_dict: dict, instId: str, timeframe: str, lenghtsSt: int):
        super().__init__()
        self.instId = instId
        self.Session = Session
        self.classes_dict = classes_dict
        self.timeframe = timeframe
        self.lenghtsSt = lenghtsSt

        
    def load_data(self):
        return DataAllDatasets.get_current_chart_data(
            self.flag, self.instId, self.timeframe, Base,
            self.Session, self.classes_dict, None, None, self.lenghtsSt
        )

    
    def load_data_for_period(self, data: pd.DataFrame):
        data = data.drop(data.index[:1])
        new_data = DataAllDatasets.get_current_chart_data(
            self.flag, self.instId, self.timeframe, Base,
            self.Session, self.classes_dict, None, None, lenghts = 1
        )
        return pd.concat([data, new_data], ignore_index=True)
