#libs
import math, statistics as stat, pandas as pd
from typing import Optional
#database
from datasets.database import DataAllDatasets
#utils
from datasets.utils.dataframe_utils import create_dataframe


class CalculateHistoricVolatility(DataAllDatasets):
    def __init__(self, timeframe:str, instId:str, data:Optional[pd.DataFrame]=None):
        self.instId = instId
        self.timeframe = timeframe
        DataAllDatasets.__init__(self, self.instId, self.timeframe)
        self.data = data


    def __prepare_data(self):
        if not self.data:
            self.data = create_dataframe(self.get_all_bd_marketdata())


    def __calc_time_interval(self):
        return (self.data.index[-1] - self.data.index[0]).days / 365.25


    # Рассчёт коэффициента волатильности(два варианта хз какой использовать) вариант 1
    def calculate_volatility_v1(self):
        self.__prepare_data
        st_dev = stat.stdev(self.data['High'] + self.data['Low'])
        data_mean = stat.mean(self.data['High'] + self.data['Low'])
        return  st_dev / data_mean * 100


    # Рассчёт коэффициента волатильности(два варианта хз какой использовать) вариант 2
    def calculate_volatility_v2(self):
        log_returns = []
        
        for i in range(len(self.data['High']) - 1, 0, -1):
            current_price = (self.data['High'][i] + self.data['Low'][i]) / 2
            previous_price = (self.data['High'][i - 1] + self.data['Low'][i - 1]) / 2
            log_return = math.log(current_price) - math.log(previous_price)
            log_returns.append(log_return)
        std_dev = math.sqrt(sum((x - sum(log_returns) / len(log_returns))**2 for x in log_returns) / (len(log_returns) - 1))
        return std_dev * math.sqrt(self.__calc_time_interval())
