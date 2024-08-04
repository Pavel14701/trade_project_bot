import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from User.LoadSettings import LoadUserSettingData
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import talib



class ADXTrend:
    def __init__(self, data:pd.DataFrame):
        settings = LoadUserSettingData.load_adx_configs()
        self.timeperiod = settings['adx_timeperiod']
        self.data = data


    def calculate_adx(self) -> pd.DataFrame:
        # Вычисляем индикатор ADX
        self.data['ADX'] = talib.ADX(
            self.data['High'].values, 
            self.data['Low'].values, 
            self.data['Close'].values, 
            self.timeperiod
            )
        print(self.data)
        return self.data['ADX'].iloc[-1], self.data


    @staticmethod
    def create_vizualization_adx(data):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        ax1.plot(data.index, data['Close'], label='Цена закрытия', color='blue')
        ax2.plot(data.index, data['ADX'], label='ADX', color='orange')
        ax1.legend()
        ax1.set_title('Визуализация ADX')
        ax1.set_xlabel('Дата')
        ax1.set_ylabel('Цена')
        plt.show()