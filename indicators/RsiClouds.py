import talib
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.widgets import Cursor


# from test_data_loading import LoadDataFromYF


class CloudsRsi:
    """Summary:
    Class for calculating and visualizing RSI Clouds.

    Explanation:
    This class provides static methods to calculate RSI values for short and long periods, smooth them using EMA, detect crossover signals, and create a visualization of the RSI Cloud indicator with buy and sell signals.

    Args:
    - data: The input data containing Close prices.
    - rsi_period_short: The short period for RSI calculation.
    - rsi_period_long: The long period for RSI calculation.
    - ema_period: The period for EMA smoothing.

    Returns:
    - For calculate_rsi_clouds: DataFrame with RSI Short EMA, RSI Long EMA, Cross Up, and Cross Down signals.
    - For create_vizualization_rsi_clouds: None
    """

    @staticmethod
    def calculate_rsi_clouds(data, rsi_period_short, rsi_period_long, ema_period):
        """Summary:
        Calculate RSI values and crossover signals for RSI Clouds.

        Explanation:
        This static method calculates RSI values for short and long periods, smoothes them using EMA, and detects crossover signals to determine buy and sell points.

        Args:
        - data: The input data containing Close prices.
        - rsi_period_short: The short period for RSI calculation.
        - rsi_period_long: The long period for RSI calculation.
        - ema_period: The period for EMA smoothing.

        Returns:
        - DataFrame with RSI Short EMA, RSI Long EMA, Cross Up, and Cross Down signals.
        """
        # Вычисляем RSI для двух периодов
        rsi_short = talib.RSI(data['Close'].values, timeperiod=rsi_period_short)
        rsi_long = talib.RSI(data['Close'].values, timeperiod=rsi_period_long)
        # Сглаживаем RSI с помощью EMA
        rsi_short_ema = talib.EMA(rsi_short, timeperiod=ema_period)
        rsi_long_ema = talib.EMA(rsi_long, timeperiod=ema_period)
        # Добавляем индикаторы в DataFrame
        data['RSI_Short_EMA'] = rsi_short_ema
        data['RSI_Long_EMA'] = rsi_long_ema
        # Сигналы пересечения
        cross_up = (data['RSI_Short_EMA'] > data['RSI_Long_EMA']) & (
                    data['RSI_Short_EMA'].shift(1) <= data['RSI_Long_EMA'].shift(1))
        cross_down = (data['RSI_Short_EMA'] < data['RSI_Long_EMA']) & (
                    data['RSI_Short_EMA'].shift(1) >= data['RSI_Long_EMA'].shift(1))
        # Добавляем сигналы в DataFrame
        data['Cross_Up'] = cross_up
        data['Cross_Down'] = cross_down
        return data

    @staticmethod
    def create_vizualization_rsi_clouds(data):
        """Summary:
        Create visualization for RSI Clouds.

        Explanation:
        This static method generates a visualization of the RSI Cloud indicator with buy and sell signals based on the provided data.

        Args:
        - data: The input data containing Close prices.

        Returns:
        None
        """
        overbought = 70
        oversold = 30
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        ax1.plot(data.index, data['Close'], label='AAPL Close Price', color='black')
        ax1.scatter(data.index[data['Cross_Up']], data['Close'][data['Cross_Up']], color='green', label='Cross Up',
                    marker='^', alpha=1)
        ax1.scatter(data.index[data['Cross_Down']], data['Close'][data['Cross_Down']], color='red', label='Cross Down',
                    marker='v', alpha=1)
        ax1.set_title('AAPL Stock Price')
        ax1.set_ylabel('Price', color='black')
        ax1.tick_params(axis='y', labelcolor='black')
        ax1.legend(loc='upper left')
        ax2.plot(data.index, data['RSI_Short_EMA'], label='RSI Short EMA (7)', color='blue')
        ax2.plot(data.index, data['RSI_Long_EMA'], label='RSI Long EMA (14)', color='orange')
        ax2.scatter(data.index[data['Cross_Up']], data['RSI_Short_EMA'][data['Cross_Up']], color='green',
                    label='Cross Up', marker='^', alpha=1)
        ax2.scatter(data.index[data['Cross_Down']], data['RSI_Short_EMA'][data['Cross_Down']], color='red',
                    label='Cross Down', marker='v', alpha=1)
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


"""
#Пример использования
data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
print(data)
data = CloudsRsi.calculate_rsi_clouds(data, rsi_period_short = 7, rsi_period_long = 14, ema_period = 9)
CloudsRsi.create_vizualization_rsi_clouds(data)
"""

