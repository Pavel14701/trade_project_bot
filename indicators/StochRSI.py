import numpy as np
import matplotlib.pyplot as plt
import talib
import pandas as pd
#from test_data_loading import LoadDataFromYF


class StochRSICalculator:
    """Summary:
    Class for calculating and visualizing Stochastic RSI (StochRSI).

    Explanation:
    This class provides static methods to calculate StochRSI values, including Fast %K and Fast %D lines, and visualize the StochRSI indicator with buy and sell signals based on the provided data.

    Args:
    - data: The input data containing Close prices.

    Returns:
    - For calculate_stochrsi: Tuple containing input data, Fast %D values, and Fast %K values.
    - For plot_stochrsi: None
    """
    
    
    @staticmethod
    def calculate_stochrsi(data):
        """Summary:
        Calculate Stochastic RSI (StochRSI) values.

        Explanation:
        This static method calculates the Stochastic RSI (StochRSI) values based on the Close prices in the provided data.

        Args:
        - data: The input data containing Close prices.

        Returns:
        - Tuple containing the input data, Fast %D values, and Fast %K values.
        """
        # Рассчитываем StochRSI
        fastk, fastd = talib.STOCHRSI(data['Close'], timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
        # Преобразуем numpy массивы в pandas Series с правильным индексом
        fastk = pd.Series(fastk, index=data.index)
        fastd = pd.Series(fastd, index=data.index)
        return (data, fastd, fastk)

    @staticmethod
    def plot_stochrsi(fastk, fastd, data):
        """Summary:
        Plot Stochastic RSI (StochRSI) with buy and sell signals.

        Explanation:
        This static method visualizes the Stochastic RSI (StochRSI) indicator with Fast %K and Fast %D lines, highlighting buy and sell signals based on the provided data.

        Args:
        - fastk: The Fast %K line values.
        - fastd: The Fast %D line values.
        - data: The input data containing Close prices.

        Returns:
        None
        """
        # Стандартные сигналы для StochRSI
        buy_signals = (fastk > fastd) & (fastk.shift(1) < fastd.shift(1)) & (fastk < 20)
        sell_signals = (fastk < fastd) & (fastk.shift(1) > fastd.shift(1)) & (fastk > 80)
        # Визуализация
        plt.figure(figsize=(14, 7))
        plt.subplot(2, 1, 1)
        plt.plot(data['Close'], label='Цена закрытия')
        plt.title('Цена закрытия')
        plt.legend()
        plt.subplot(2, 1, 2)
        plt.plot(fastk, label='Fast %K line', color='blue')
        plt.plot(fastd, label='Fast %D line', color='orange')
        plt.fill_between(data.index, fastk, fastd, where=fastk > fastd, color='lightgreen', alpha=0.5)
        plt.fill_between(data.index, fastk, fastd, where=fastk < fastd, color='lightcoral', alpha=0.5)
        plt.plot(data.index[buy_signals], fastk[buy_signals], '^', markersize=10, color='g', lw=0, label='Сигнал к покупке')
        plt.plot(data.index[sell_signals], fastk[sell_signals], 'v', markersize=10, color='r', lw=0, label='Сигнал к продаже')
        plt.title('Stochastic RSI (StochRSI)')
        plt.legend()
        plt.tight_layout()
        plt.show()

"""
#Пример использования
data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
print(data)
data, fastd, fastk = StochRSICalculator.calculate_stochrsi(data)
StochRSICalculator.plot_stochrsi(fastk, fastd, data)
"""
