from database import DataAllDatasets, Base
import pandas as pd
from utils.DataLoadSettings import DataLoadSetting

class StreamData(DataLoadSetting):
    def __init__(self):
        super().__init__(self.lenghts, self.instId, self.timeframe, self.flag)
    
        
    def load_data(self, Session, classes_dict):
        return DataAllDatasets.get_current_chart_data(
            self.flag, self.instId, self.timeframe, Base,
            Session, classes_dict, None, None, self.lenghts
        )
    
    
    def load_data_for_period(self, Session, classes_dict, data):
        data = data.drop(data.index[:1])
        new_data = DataAllDatasets.get_current_chart_data(
            self.flag, self.instId, self.timeframe, Base,
            Session, classes_dict, None, None, lenghts = 1
        )
        return pd.concat([data, new_data], ignore_index=True)

