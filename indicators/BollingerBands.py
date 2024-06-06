import matplotlib.pyplot as plt
import talib
import numpy as np


# from test_data_loading import LoadDataFromYF

class BollindgerBands:
    """
    A class for calculating and visualizing Bollinger Bands on stock price data.

    Methods:
    - calculate_bands(data, lenghts, stdev): Calculates Bollinger Bands based on the given data, lengths, and standard deviations.
    - create_vizualization_bb(data): Creates a visualization of stock price with Bollinger Bands.
    - generate_signals(data): Generates trading signals based on Bollinger Bands.
    - create_vizualization_bb_with_signals(data): Creates a visualization of stock price with Bollinger Bands and trading signals.
    """

    @staticmethod
    def calculate_bands(data, lenghts, stdev):
        """
        Calculates Bollinger Bands based on the given data, lengths, and standard deviations.

        Args:
        - data (DataFrame): Input data containing 'High' and 'Low' prices.
        - lenghts (int): Length of the moving average window.
        - stdev (int): Standard deviation multiplier for the bands.

        Returns:
        - DataFrame: Data with added columns for Upper Band, Middle Band, and Lower Band.
        """
        high_low_average = (data['High'] + data['Low']) / 2
        upper_band, middle_band, lower_band = talib.BBANDS(
            high_low_average,
            timeperiod=lenghts,
            nbdevup=stdev,
            nbdevdn=stdev,
            matype=0
        )
        data['Upper Band'] = upper_band
        data['Middle Band'] = middle_band
        data['Lower Band'] = lower_band
        return data

    @staticmethod
    def create_vizualization_bb(data):
        """
        Creates a visualization of stock price with Bollinger Bands.

        Args:
        - data (DataFrame): Input data containing 'Close', 'Upper Band', 'Middle Band', and 'Lower Band' values.

        Returns:
        None
        """
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.plot(data.index, data['Close'], label='Цена закрытия', color='blue')
        ax.plot(data.index, data['Upper Band'], label='Верхняя полоса', color='red', linestyle='--')
        ax.plot(data.index, data['Middle Band'], label='Средняя полоса', color='black', linestyle='-.')
        ax.plot(data.index, data['Lower Band'], label='Нижняя полоса', color='green', linestyle='--')
        ax.fill_between(data.index, data['Upper Band'], data['Lower Band'], color='grey', alpha=0.1)
        ax.legend()
        ax.set_title('Визуализация полос Боллинджера')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Цена')
        plt.show()

    @staticmethod
    def generate_signals(data):
        """
        Generates trading signals based on the position of the closing price relative to the Bollinger Bands.

        Args:
        - data (DataFrame): Input data containing 'Close', 'Upper Band', 'Middle Band', and 'Lower Band'.

        Returns:
        - DataFrame: Data with added columns for Buy Signal and Sell Signal.
        """
        buy_signal = []
        sell_signal = []
        for i in range(len(data)):
            if data['Close'][i] < data['Lower Band'][i]:
                buy_signal.append(data['Close'][i])
                sell_signal.append(np.nan)
            elif data['Close'][i] > data['Upper Band'][i]:
                sell_signal.append(data['Close'][i])
                buy_signal.append(np.nan)
            else:
                buy_signal.append(np.nan)
                sell_signal.append(np.nan)

        data['Buy Signal'] = buy_signal
        data['Sell Signal'] = sell_signal
        return data

    @staticmethod
    def create_vizualization_bb_with_signals(data):
        """
        Creates a visualization of stock price with Bollinger Bands and trading signals.

        Args:
        - data (DataFrame): Input data containing 'Close', 'Upper Band', 'Middle Band', 'Lower Band', 'Buy Signal', and 'Sell Signal'.

        Returns:
        None
        """
        fig, ax = plt.subplots(figsize=(14, 7))
        # Existing code for visualization
        ax.plot(data.index, data['Close'], label='Цена закрытия', color='blue')
        ax.plot(data.index, data['Upper Band'], label='Верхняя полоса', color='red', linestyle='--')
        ax.plot(data.index, data['Middle Band'], label='Средняя полоса', color='black', linestyle='-.')
        ax.plot(data.index, data['Lower Band'], label='Нижняя полоса', color='green', linestyle='--')
        ax.fill_between(data.index, data['Upper Band'], data['Lower Band'], color='grey', alpha=0.1)
        # Signals visualization
        ax.scatter(data.index, data['Buy Signal'], label='Сигнал к покупке', marker='^', color='green')
        ax.scatter(data.index, data['Sell Signal'], label='Сигнал к продаже', marker='v', color='red')
        ax.legend()
        plt.show()

# Пример использования новых методов
# data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
# print(data)
# data = BollindgerBands.calculate_bands(data, lenghts=34, stdev=2)
# print(data)
# data = BollindgerBands.generate_signals(data)
# BollindgerBands.create_vizualization_bb_with_signals(data)
