import talib
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.widgets import Cursor
from User.LoadSettings import LoadUserSettingData
from pandas import DataFrame


class CloudsRsi(LoadUserSettingData):
    def __init__(self, data:DataFrame):
        super().__init__()
        data.self = data
        self.rsi_period_short = self.rsi_configs['rsi_period_short']
        self.rsi_period_long = self.rsi_configs['rsi_period_long']
        self.ema_period = self.rsi_configs['ema_period']
        

    def calculate_rsi_clouds(self):
        rsi_short = talib.RSI(self.data['Close'].values, timeperiod=self.rsi_period_short)
        rsi_long = talib.RSI(self.data['Close'].values, timeperiod=self.rsi_period_long)
        rsi_short_ema = talib.EMA(rsi_short, timeperiod=self.ema_period)
        rsi_long_ema = talib.EMA(rsi_long, timeperiod=self.ema_period)
        self.data['RSI_Short_EMA'] = rsi_short_ema
        self.data['RSI_Long_EMA'] = rsi_long_ema
        cross_up = (self.data['RSI_Short_EMA'] > self.data['RSI_Long_EMA']) & (self.data['RSI_Short_EMA'].shift(1) <= self.data['RSI_Long_EMA'].shift(1))
        cross_down = (self.data['RSI_Short_EMA'] < self.data['RSI_Long_EMA']) & (self.data['RSI_Short_EMA'].shift(1) >= self.data['RSI_Long_EMA'].shift(1))
        self.data['Cross_Up'] = cross_up
        self.data['Cross_Down'] = cross_down
        last_bar_signal = None
        if cross_up[-1]:
            last_bar_signal = 'cross_up'
        elif cross_down[-1]:
            last_bar_signal = 'cross_down'
        return last_bar_signal


    @staticmethod
    def create_vizualization_rsi_clouds(data) -> plt:
        overbought = 70
        oversold = 30
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        ax1.plot(data.index, data['Close'], label='AAPL Close Price', color='black')
        ax1.scatter(data.index[data['Cross_Up']], data['Close'][data['Cross_Up']], color='green', label='Cross Up', marker='^', alpha=1)
        ax1.scatter(data.index[data['Cross_Down']], data['Close'][data['Cross_Down']], color='red', label='Cross Down', marker='v', alpha=1)
        ax1.set_title('AAPL Stock Price')
        ax1.set_ylabel('Price', color='black')
        ax1.tick_params(axis='y', labelcolor='black')
        ax1.legend(loc='upper left')
        ax2.plot(data.index, data['RSI_Short_EMA'], label='RSI Short EMA (7)', color='blue')
        ax2.plot(data.index, data['RSI_Long_EMA'], label='RSI Long EMA (14)', color='orange')
        ax2.scatter(data.index[data['Cross_Up']], data['RSI_Short_EMA'][data['Cross_Up']], color='green', label='Cross Up', marker='^', alpha=1)
        ax2.scatter(data.index[data['Cross_Down']], data['RSI_Short_EMA'][data['Cross_Down']], color='red', label='Cross Down', marker='v', alpha=1)
        ax2.axhline(y=overbought, color='darkred', linestyle='--', label='Overbought (70)')
        ax2.axhline(y=oversold, color='darkgreen', linestyle='--', label='Oversold (30)')
        ax2.set_title('RSI Cloud Indicator with Signals')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('RSI Value', color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')
        ax2.legend(loc='upper right')
        mplcursors.cursor(hover=True)
        plt.tight_layout()
        plt.show()
