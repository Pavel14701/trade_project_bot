import pandas as pd
import pandas_ta as ta
from User.LoadSettings import LoadUserSettingData
import matplotlib.pyplot as plt

class MesaAdaptiveMA:
    def __init__(self, data: pd.DataFrame):
        settings = LoadUserSettingData.load_mesa_adaptive_ma_configs()
        self.fastlimit = settings['mesa_fastlimit'] #0.5
        self.slowlimit = settings['mesa_slowlimit'] #0.05
        self.prenan = settings['mesa_prenan']
        self.talib = settings['mesa_talib']
        self.offset = settings['mesa_offset']
        self.data = data


    def calculate_mama(self):
        mama, fama = ta.mama(self.data['Close'], fastlimit=self.fastlimit, slowlimit=self.slowlimit, prenan=self.prenan, talib=self.talib, offset=self.offset)
        self.data['MAMA'] = mama
        self.data['FAMA'] = fama
        #Cигналы для покупки и продажи
        self.buy_signals = (mama > fama) & (mama.shift(1) < fama.shift(1))
        self.sell_signals = (mama < fama) & (mama.shift(1) > fama.shift(1))
        return {'data': self.data, 'buy_signals': self.buy_signals, 'sell_signals': self.sell_signals}
    
    
    @staticmethod
    def plot_mama(self):
        # Визуализируем данные
        plt.figure(figsize=(10, 5))
        plt.plot(self.data['Close'], label='Close Price')
        plt.plot(self.data['MAMA'], label='MAMA', color='red')
        plt.plot(self.data['FAMA'], label='FAMA', color='green')
        # Добавляем сигналы на график
        plt.plot(self.data.index[self.buy_signals], self.data['Close'][self.buy_signals], '^', markersize=10, color='g', lw=0, label='Buy Signal')
        plt.plot(self.data.index[self.sell_signals], self.data['Close'][self.sell_signals], 'v', markersize=10, color='r', lw=0, label='Sell Signal')
        plt.title('MESA Adaptive Moving Average (MAMA) and FAMA')
        plt.legend()
        plt.show()