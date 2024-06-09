import numpy as np
import matplotlib.pyplot as plt
from test_data_loading import LoadDataFromYF
from graphics.IndicatorDrawer import IndicatorDrawer


class KAMA:
    """
    A class for calculating and visualizing KAMA (Kaufman's Adaptive Moving Average) indicators on stock price data.

    Methods:
    - kama(data, period, fast, slow): Calculates the KAMA values based on the given data, period, fast, and slow parameters.
    - calculate_kama(data, period, fast, slow): Calculates KAMA values and adds them to the input data.
    - create_visualization_kama(data): Creates a visualization of stock price with KAMA indicator.
    """

    @staticmethod
    def kama(data, period, fast, slow):
        """
        Calculates the Kaufman's Adaptive Moving Average (KAMA) values based on the given data, period, fast, and slow parameters.

        Args:
        - data (DataFrame): Input data containing 'High' and 'Low' prices.
        - period (int): Period for calculating KAMA. 54 Defolt
        - fast (int): Fast smoothing constant. 3 Defolt
        - slow (int): Slow smoothing constant. 34 Defolt

        Returns:
        - array: Array of KAMA values.
        """
        # Вычисляем направление и волатильность
        direction = abs(((data['High'] - data['High'].shift(period)) + (data['Low'] - data['Low'].shift(period))) / 2)
        volatility = (data['High'].diff().abs().rolling(period).sum() + data['Low'].diff().abs().rolling(
            period).sum()) / 2 + 0.0001  # добавим небольшое число к волатильности
        # Вычисляем коэффициент эффективности
        er = direction / volatility
        # Вычисляем сглаживающую константу
        sc = (er * (2 / (fast + 1) - 2 / (slow + 1)) + 2 / (slow + 1)) ** 2
        # Вычисляем KAMA
        kama = np.zeros(len(data))
        kama[period] = (data['High'].iloc[period] + data['Low'].iloc[period]) / 2  # используем среднее между high и low
        for i in range(period + 1, len(data)):
            # используем .iloc[] для sc
            kama[i] = kama[i - 1] + sc.iloc[i] * ((data['High'].iloc[i] + data['Low'].iloc[i]) / 2 - kama[i - 1])
        return kama

    @staticmethod
    def calculate_kama(data, period, fast, slow):
        # Добавляем колонку с KAMA в датафрейм
        data['KAMA'] = KAMA.kama(data, period, fast, slow)

        # Генерация сигналов покупки и продажи
        data['Signal'] = 0  # Инициализация колонки сигналов
        data.loc[data['Close'] > data['KAMA'], 'Signal'] = 1  # Сигнал на покупку
        data.loc[data['Close'] < data['KAMA'], 'Signal'] = -1  # Сигнал на продажу

        return data


# Пример использования
data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
print(data)
data = KAMA.calculate_kama(data, period=54, fast=3, slow=34)
IndicatorDrawer.draw_kama(data)
