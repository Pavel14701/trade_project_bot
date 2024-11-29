#libs
import asyncio, pandas as pd, numpy as np, matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from pandas_ta import rsi, macd
from typing import Optional
#configs
from configs.load_settings import ConfigsProvider


class CloudsRsi:
    def __init__(self, data:pd.DataFrame, return_pd:Optional[bool]=None):
        settings = ConfigsProvider().load_rsi_clouds_configs()
        self.rsi_period = settings['rsi_period']
        self.rsi_scalar = settings['rsi_scalar']
        self.rsi_drift =settings['rsi_drift']
        self.rsi_offset = settings['rsi_offset']
        self.rsi_mamode = settings['rsi_mamode']
        self.rsi_talib_config = settings['rsi_talib_config']
        self.macd_fast = settings['macd_fast']
        self.macd_slow = settings['macd_slow']
        self.macd_signal = settings['macd_signal']
        self.macd_offset = settings['macd_offset']
        self.macd_talib_config = settings['macd_talib_config']
        self.calc_data = settings['calc_data']
        self.data = data
        self.return_pd = return_pd


    def prepare_data(self):
        try:
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
        except KeyError as e:
            raise e(f"Missing required column: {e}") from e


    def calculate_rsi_macd(self) -> pd.DataFrame:
        self.prepare_data()
        self.data['rsi'] = rsi(
            self.data['pr_data'], length=self.rsi_period, scalar=self.rsi_scalar,
            mamode=self.rsi_mamode, talib=self.rsi_talib_config, drift=self.rsi_drift,
            offset=self.rsi_drift
        )
        macd_ind = macd(
            self.data['rsi'], fast=self.macd_fast, slow=self.macd_slow, signal=self.macd_signal,
            talib=self.macd_talib_config, offset=self.macd_offset
        )
        self.data['macd_line'] = macd_ind[f'MACD_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}']
        self.data['macd_signal'] = macd_ind[f'MACDs_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}']
        self.data['histogram'] = macd_ind[f'MACDh_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}']
        self.data['macd_cross_signal'] = 0
        self.data['histogram_cross_zero'] = 0
        # Логика пересечения MACD
        self.data['macd_cross_signal'] = np.where(
            (self.data['macd_line'].shift(1) < self.data['macd_signal'].shift(1)) \
                    & (self.data['macd_line'] > self.data['macd_signal']), 1, 
            np.where((self.data['macd_line'].shift(1) > self.data['macd_signal'].shift(1)) \
                    & (self.data['macd_line'] < self.data['macd_signal']), -1, 0)
        )
        # Логика пересечения нуля на гистограмме
        self.data['histogram_cross_zero'] = np.where(
            (self.data['histogram'].shift(1) < 0) & (self.data['histogram'] > 0), 1, 
            np.where((self.data['histogram'].shift(1) > 0) & (self.data['histogram'] < 0), -1, 0)
        )
        last_signal = self.get_last_macd_signal()
        return self.data if self.return_pd else last_signal

    def get_last_macd_signal(self):
        # Получение последнего сигнала пересечения MACD
        return None if self.data['macd_cross_signal'].replace(0, np.nan).dropna().empty \
            else self.data['macd_cross_signal'].replace(0, np.nan).dropna().iloc[-1]


    async def calculate_rsi_macd_async(self) -> pd.DataFrame:
        # sourcery skip: inline-immediately-returned-variable
        executor = ThreadPoolExecutor()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, self.calculate_rsi_macd)
        return result


    def create_visualization_rsi_macd(self):
        self.data, last_signal = self.calculate_rsi_macd()
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
