import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from User.LoadSettings import LoadUserSettingData
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import talib


class ADXTrend(LoadUserSettingData):
    def __init__(self, data:pd.DataFrame):
        super.__init__()
        self.data = data
        self.timeperiod = self.adx_timeperiod
        
    def calculate_adx(self) -> pd.DataFrame:
        # Вычисляем индикатор ADX
        self.data['ADX'] = talib.ADX(
            self.data['High'].values, 
            self.data['Low'].values, 
            self.data['Close'].values, 
            self.timeperiod
            )
        return self.data['ADX'][-1]
