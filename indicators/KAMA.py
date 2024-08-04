import numpy as np
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
from User.LoadSettings import LoadUserSettingData
#from test_data_loading import LoadDataFromYF


class KAMAIndicator:
    def __init__(self, data: pd.DataFrame):
        settings = LoadUserSettingData.load_kama_configs()
        self.lengths = settings['kama_lengths']
        self.fast = settings['kama_fast']
        self.slow = settings['kama_slow']
        self.drift = settings['kama_drift']
        self.offset = settings['kama_offset']
        self.data = data


    def calculate_kama(self):
        self.data['HL'] = (self.data['High'] + self.data['Low']) / 2
        self.data['KAMA'] = ta.kama(self.data['HL'], length=self.lengths, fast=self.fast, slow=self.slow, drift=self.drift, offset=self.offset)
    

    def create_visualization_kama(self):
        plt.figure(figsize=(12,8))
        plt.plot(self.data['Close'], label='Price')
        plt.plot(self.data['KAMA'], label='KAMA')
        plt.title('Price and KAMA')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.show()