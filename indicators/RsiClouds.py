import pandas_ta as ta
import talib
import matplotlib.pyplot as plt
from User.LoadSettings import LoadUserSettingData
import pandas as pd
import numpy as np

from User.UserInfoFunctions import UserInfo
from utils.DataFrameUtils import prepare_many_data_to_append_db, create_dataframe


class CloudsRsi(LoadUserSettingData):
    def __init__(self, data:pd.DataFrame):
        super().__init__()
        self.data = data
        self.rsi_period = self.clouds_rsi_configs['rsi_period']
        self.rsi_scalar = self.clouds_rsi_configs['rsi_scalar']
        self.rsi_drift =self.clouds_rsi_configs['rsi_drift']
        self.rsi_offset = self.clouds_rsi_configs['rsi_offset']
        self.macd_fast = self.clouds_rsi_configs['macd_fast']
        self.macd_slow = self.clouds_rsi_configs['macd_slow']
        self.macd_signal = self.clouds_rsi_configs['macd_signal']
        self.macd_offset = self.clouds_rsi_configs['macd_offset']
        self.calc_data = self.clouds_rsi_configs['calc_data']
        self.talib_config = self.clouds_rsi_configs['talib']


    def prepare_data(self):
        if self.calc_data == 'Open/Close':
            self.data['pr_data'] = (self.data['Open'] + self.data['Close']) / 2
        elif self.calc_data == 'High/Low':
            self.data['pr_data'] = (self.data['High'] + self.data['Low']) / 2
        elif self.calc_data == 'Open':
            self.data['pr_data'] = self.data['Open']
        elif self.calc_data == 'Close':
            self.data['pr_data'] = self.data['Close']
        elif self.calc_data == 'High':
            self.data['pr_data'] = self.data['High']
        else:
            raise ValueError(f"Invalid calc_data value: {self.calc_data}")
        self.data['pr_data'] = self.data['pr_data'].astype(np.float64)


def calculate_rsi_macd(self) -> pd.DataFrame:
    try:
        self.prepare_data()
        self.data['rsi'] = ta.rsi(self.data['pr_data'], length=self.rsi_period, scalar=self.rsi_scalar, talib=self.talib_config, drift=self.rsi_drift, offset=self.rsi_drift)
        return self.data
    except KeyError as e:
        raise ValueError(f"Missing required column: {e}")
    except Exception as e:
        raise RuntimeError(f"Error calculating RSI MACD: {e}")
        self.prepare_data()
        self.data['rsi'] = ta.rsi(self.data['pr_data'], length=self.rsi_period, scalar=self.rsi_scalar, talib=self.talib_config, drift=self.rsi_drift, offset=self.rsi_drift)
        macd = ta.macd(self.data['rsi'], fast=self.macd_fast, slow=self.macd_slow, signal=self.macd_signal, talib=self.talib_config, offset=self.macd_offset)
        self.data['macd_line'] = macd[f'MACD_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}']
        self.data['macd_signal'] = macd[f'MACDs_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}']
        self.data['histogram'] = macd[f'MACDh_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}']
        self.data['macd_cross_signal'] = 0
        self.data['histogram_cross_zero'] = 0
        # Логика пересечения MACD
        self.data['macd_cross_signal'] = np.where(
            (self.data['macd_line'].shift(1) < self.data['macd_signal'].shift(1)) & (self.data['macd_line'] > self.data['macd_signal']), 1, 
            np.where((self.data['macd_line'].shift(1) > self.data['macd_signal'].shift(1)) & (self.data['macd_line'] < self.data['macd_signal']), -1, 0)
        )
        # Логика пересечения нуля на гистограмме
        self.data['histogram_cross_zero'] = np.where(
            (self.data['histogram'].shift(1) < 0) & (self.data['histogram'] > 0), 1, 
            np.where((self.data['histogram'].shift(1) > 0) & (self.data['histogram'] < 0), -1, 0)
        )
        return self.get_last_macd_signal()

    def get_last_macd_signal(self):
        # Получение последнего сигнала пересечения MACD
        return None if self.data['macd_cross_signal'].replace(0, np.nan).dropna().empty else self.data['macd_cross_signal'].replace(0, np.nan).dropna().iloc[-1]


    def create_visualization_rsi_macd(self):
        # Создание подграфиков
        fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(10, 12))
        # График цены
        axes[0].plot(self.data.index, self.data['Close'], label='Цена')
        axes[0].set_title('Цена')
        # График RSI
        axes[1].plot(self.data.index, self.data['rsi'], label='RSI')
        axes[1].set_title('RSI')
        # График MACD
        axes[2].plot(self.data.index, self.data['macd_line'], label='MACD Line', color='blue')
        axes[2].plot(self.data.index, self.data['macd_signal'], label='Signal Line', color='orange')
        axes[2].set_title('MACD')
        # Гистограмма MACD
        axes[3].bar(self.data.index, self.data['histogram'], label='MACD Histogram', color='purple')
        axes[3].set_title('MACD Histogram')
        # Добавление сигналов
        buy_signals = self.data[self.data['macd_cross_signal'] == 1]
        sell_signals = self.data[self.data['macd_cross_signal'] == -1]
        zero_crossings = self.data[self.data['histogram_cross_zero'] != 0]
        axes[2].scatter(buy_signals.index, buy_signals['macd_line'], color='green', marker='^', label='Buy Signal')
        axes[2].scatter(sell_signals.index, sell_signals['macd_line'], color='red', marker='v', label='Sell Signal')
        axes[3].scatter(zero_crossings.index, zero_crossings['histogram'], color='black', marker='o', label='Zero Crossing')
        # Оформление графиков
        for ax in axes:
            ax.grid(True)
            ax.legend()
            ax.set_xlabel('Date')
        plt.tight_layout()
        plt.show()
        return self.data
        
        
result = UserInfo('BTC-USDT-SWAP', '4H', 300).get_market_data(300)
data = prepare_many_data_to_append_db(result)
data = create_dataframe(data)
instance = CloudsRsi(data)
signal = instance.calculate_rsi_macd()
print(signal)
data = instance.create_visualization_rsi_macd()
print(data)
