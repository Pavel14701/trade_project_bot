#libs
import asyncio, talib, pandas as pd, matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
#configs
from configs.load_settings import ConfigsProvider


'''
from Api.OKXInfo import OKXInfoFunctions
from DataSets.Utils.DataFrameUtils import create_dataframe, prepare_many_data_to_append_db
'''

class StochRSICalculator:
    def __init__(self, data: pd.DataFrame):
        settings = ConfigsProvider().load_stoch_rsi_configs()
        self.timeperiod = settings['stoch_rsi_timeperiod']
        self.fastk_period = settings['stoch_rsi_fastk_period']
        self.fastd_period = settings['stoch_rsi_fastd_period']
        self.fastd_matype = settings['stoch_rsi_fastd_matype']
        self.data = data
    
    
    def calculate_stochrsi(self):
        # Рассчитываем StochRSI
        fastk, fastd = talib.STOCHRSI(self.data['Close'], self.timeperiod, self.fastk_period, self.fastd_period, self.fastd_matype)
        # Преобразуем numpy массивы в pandas Series с правильным индексом
        self.data['fastk'] = pd.Series(fastk, index=self.data.index)
        self.data['fastd'] = pd.Series(fastd, index=self.data.index)
        self.data['Cross_up'] = (self.data['fastk'] > self.data['fastd']) \
            & (self.data['fastk'].shift(1) < self.data['fastd'].shift(1)) & (self.data['fastk'] < 20)
        self.data['Cross_down'] = (self.data['fastk'] < self.data['fastd']) \
            & (self.data['fastk'].shift(1) > self.data['fastd'].shift(1)) & (self.data['fastk'] > 80)
        last_bar_signal = None
        if self.data['Cross_up'].any() and self.data['Cross_up'].iloc[-1]:
            last_bar_signal = 'long'
        if self.data['Cross_down'].any() and self.data['Cross_down'].iloc[-1]:
            last_bar_signal = 'short'
        return {
            'data': self.data, 'last_bar_signal': last_bar_signal}


    async def calculate_stochrsi_async(self) -> dict:
        # sourcery skip: inline-immediately-returned-variable
        executor = ThreadPoolExecutor()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, self.calculate_stochrsi)
        return result


    def plot_stochrsi(self):
        indicator = self.calculate_stochrsi()
        plt.figure(figsize=(14, 7))
        plt.subplot(2, 1, 1)
        plt.plot(self.data['Close'], label='Цена закрытия')
        plt.plot(self.data.index[self.data['Cross_up']],\
            self.data['fastk'][self.data['Cross_up']], \
                '^', markersize=10, color='g', lw=0)
        plt.plot(self.data.index[self.data['Cross_down']],\
            self.data['fastk'][self.data['Cross_down']],\
                'v', markersize=10, color='r', lw=0)
        plt.title('Цена закрытия')
        plt.legend()
        plt.subplot(2, 1, 2)
        plt.plot(self.data['fastk'], label='Fast %K line', color='blue')
        plt.plot(self.data['fastd'], label='Fast %D line', color='orange')
        plt.fill_between(self.data.index, self.data['fastk'], self.data['fastd'],\
            where=self.data['fastk'] > self.data['fastd'], color='lightgreen', alpha=0.5)
        plt.fill_between(self.data.index, self.data['fastk'], self.data['fastd'],\
            where=self.data['fastk'] < self.data['fastd'], color='lightcoral', alpha=0.5)
        plt.plot(self.data.index[self.data['Cross_up']],\
            self.data['fastk'][self.data['Cross_up']], '^', markersize=10,\
                color='g', lw=0, label='Сигнал к покупке')
        plt.plot(self.data.index[self.data['Cross_down']],\
            self.data['fastk'][self.data['Cross_down']], 'v', markersize=10,\
                color='r', lw=0, label='Сигнал к продаже')
        plt.title('Stochastic RSI (StochRSI)')
        plt.legend()
        plt.tight_layout()
        plt.show()
        

'''
result = OKXInfoFunctions('BTC-USDT-SWAP', '1D', 300).get_market_data(300)
data = prepare_many_data_to_append_db(result)
data = create_dataframe(data)
data = StochRSICalculator(data).calculate_stochrsi()
StochRSICalculator.plot_stochrsi(data['data'])
'''