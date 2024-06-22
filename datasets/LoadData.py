from database import DataAllDatasets, Base
import pandas as pd


class StreamData:
    
    def __init__(self, lengths, instId, timeframe, flag):
        super().__init__(lengths, instId, timeframe, flag)
        
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