import numpy as np
import matplotlib.pyplot as plt
import talib
import pandas as pd
from User.LoadSettings import LoadUserSettingData


from User.UserInfoFunctions import UserInfo
from utils.DataFrameUtils import create_dataframe, prepare_many_data_to_append_db


class StochRSICalculator(LoadUserSettingData):
    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self.data = data
        self.timeperiod = self.stoch_rsi_configs['stoch_rsi_timeperiod']
        self.fastk_period = self.stoch_rsi_configs['stoch_rsi_fastk_period']
        self.fastd_period = self.stoch_rsi_configs['stoch_rsi_fastd_period']
        self.fastd_matype = self.stoch_rsi_configs['stoch_rsi_fastd_matype']
    
    
    def calculate_stochrsi(self):
        # Рассчитываем StochRSI
        fastk, fastd = talib.STOCHRSI(self.data['Close'], self.timeperiod, self.fastk_period, self.fastd_period, self.fastd_matype)
        # Преобразуем numpy массивы в pandas Series с правильным индексом
        self.data['fastk'] = pd.Series(fastk, index=self.data.index)
        self.data['fastd'] = pd.Series(fastd, index=self.data.index)
        self.data['Cross_up_RSIClouds'] = (self.data['fastk'] > self.data['fastd']) & (self.data['fastk'].shift(1) < self.data['fastd'].shift(1)) & (self.data['fastk'] < 20)
        self.data['Cross_down_RSIClouds'] = (self.data['fastk'] < self.data['fastd']) & (self.data['fastk'].shift(1) > self.data['fastd'].shift(1)) & (self.data['fastk'] > 80)
        last_bar_signal = None
        if self.data['Cross_up_RSIClouds'].any() and self.data['Cross_up_RSIClouds'].iloc[-1]:
            last_bar_signal = 'long'
        if self.data['Cross_down_RSIClouds'].any() and self.data['Cross_down_RSIClouds'].iloc[-1]:
            last_bar_signal = 'short'
        return {
            'data': self.data, 'last_bar_signal': last_bar_signal}

    @staticmethod
    def plot_stochrsi(data):
        buy_signals = (data['fastk'] > data['fastd']) & (data['fastk'].shift(1) < data['fastd'].shift(1)) & (data['fastk'] < 20)
        sell_signals = (data['fastk'] < data['fastd']) & (data['fastk'].shift(1) > data['fastd'].shift(1)) & (data['fastk'] > 80)
        plt.figure(figsize=(14, 7))
        plt.subplot(2, 1, 1)
        plt.plot(data['Close'], label='Цена закрытия')
        plt.plot(data.index[buy_signals], data['fastk'][buy_signals], '^', markersize=10, color='g', lw=0)
        plt.plot(data.index[sell_signals], data['fastk'][sell_signals], 'v', markersize=10, color='r', lw=0)
        plt.title('Цена закрытия')
        plt.legend()
        plt.subplot(2, 1, 2)
        plt.plot(data['fastk'], label='Fast %K line', color='blue')
        plt.plot(data['fastd'], label='Fast %D line', color='orange')
        plt.fill_between(data.index, data['fastk'], data['fastd'], where=data['fastk'] > data['fastd'], color='lightgreen', alpha=0.5)
        plt.fill_between(data.index, data['fastk'], data['fastd'], where=data['fastk'] < data['fastd'], color='lightcoral', alpha=0.5)
        plt.plot(data.index[buy_signals], data['fastk'][buy_signals], '^', markersize=10, color='g', lw=0, label='Сигнал к покупке')
        plt.plot(data.index[sell_signals], data['fastk'][sell_signals], 'v', markersize=10, color='r', lw=0, label='Сигнал к продаже')
        plt.title('Stochastic RSI (StochRSI)')
        plt.legend()
        plt.tight_layout()
        plt.show()
        


result = UserInfo('BTC-USDT-SWAP', '1D', 300).get_market_data(300)
data = prepare_many_data_to_append_db(result)
data = create_dataframe(data)
data = StochRSICalculator(data).calculate_stochrsi()
StochRSICalculator.plot_stochrsi(data['data'])