import numpy as np
import talib
import matplotlib.pyplot as plt
import pandas as pd
#from test_data_loading import LoadDataFromYF


class AVSLIndicator:
    """
    A class for calculating and visualizing AVSL indicators based on volume and price data.

    Methods:
    - price_fun(VPC, VPR, VM, src): Calculates the stop-loss step based on volume, price, and source data.
    - prepare_calculate_avsl(data): Prepares data and parameters for AVSL calculation.
    - calculate_avsl(data): Calculates AVSL indicators based on the provided data.
    - avsl_visualization(cross_up, cross_down, AVSL, close_prices, data): Visualizes AVSL indicators with price data.
    """

    # Функция для расчета stop-loss шага в зависимости от объема и минимальной цены

    @staticmethod
    def price_fun(VPC, VPR, VM, src):
        """
        Calculates the price step based on volume, price, and source data.

        Args:
        - VPC (array): Array of VPC values.
        - VPR (array): Array of VPR values.
        - VM (array): Array of VM values.
        - src (array): Source data array.

        Returns:
        - PriceV (array): Array of calculated price steps.
        """
        PriceV = np.zeros_like(VPC)  # Создаем массив нулей той же формы, что и VPC
        for i in range(len(VPC)):
            VPCI = VPC[i] * VPR[i] * VM[i]
            if np.isnan(VPCI):  # Проверяем, является ли VPCI NaN
                lenV = 0
            else:
                lenV = int(round(abs(VPCI - 3))) if VPC[i] < 0 else round(VPCI + 3)
            VPCc = -1 if (-1 < VPC[i] < 0) else 1 if (1 > VPC[i] >= 0) else VPC[i]
            Price = np.sum(src[i - lenV + 1:i + 1] / VPCc / VPR[i - lenV + 1:i + 1]) if lenV > 0 else src[i]
            PriceV[i] = Price / lenV / 100 if lenV > 0 else Price
        return PriceV

    @staticmethod
    def prepare_calculate_avsl(data):
        """
        Prepares data and parameters for calculating AVSL indicators.

        Args:
        - data (DataFrame): Input data containing 'Adj Close', 'Low', and 'Volume' columns.

        Returns:
        - Tuple: A tuple containing processed data and parameters for AVSL calculation.
        """
        # Подготовка данных
        close_prices = data['Close'].values.astype('float64')
        low_prices = data['Low'].values.astype('float64')
        volumes = data['Volume'].values.astype('float64')
        # Параметры
        lenghtsFast = 34  # Быстрая скользящая средняя
        lenghtsSlow = 134  # Медленная скользящая средняя
        lenT = 9  # Сигнал для VPCI
        standDiv = 3.0  # Стандартное отклонение
        offset = 2  # Смещение
        # Расчеты
        VWmaS = talib.WMA(close_prices, timeperiod=lenghtsSlow)  # Медленная VWMA
        VWmaF = talib.WMA(close_prices, timeperiod=lenghtsFast)  # Быстрая VWMA
        AvgS = talib.SMA(close_prices, timeperiod=lenghtsSlow)  # Медленная средняя объема
        AvgF = talib.SMA(close_prices, timeperiod=lenghtsFast)  # Быстрая средняя объема
        VPC = VWmaS - AvgS  # VPC+/-
        VPR = VWmaF / AvgF  # Отношение цены к объему
        VM = talib.SMA(volumes, timeperiod=lenghtsFast) / talib.SMA(volumes, timeperiod=lenghtsSlow)  # Множитель объема
        VPCI = VPC * VPR * VM  # Индикатор VPCI
        DeV = standDiv * VPCI * VM  # Отклонение
        return close_prices, DeV, low_prices, VPC, VPR, VM, lenghtsSlow

    @staticmethod
    def calculate_avsl(data):
        """
        Calculates AVSL indicators based on the provided data.

        Args:
        - data (DataFrame): Input data containing 'Adj Close', 'Low', and 'Volume' columns.

        Returns:
        - Tuple: A tuple containing cross up, cross down signals, AVSL values, close prices and signal at last bar.
        """
        close_prices, DeV, low_prices, VPC, VPR, VM, lenghtsSlow = AVSLIndicator.prepare_calculate_avsl(data)
        PriceV = AVSLIndicator.price_fun(VPC, VPR, VM, low_prices)
        AVSL = talib.SMA(low_prices - PriceV + DeV, timeperiod=lenghtsSlow)
        cross_up = (close_prices > AVSL) & (np.roll(close_prices, 1) <= np.roll(AVSL, 1))
        cross_down = (close_prices < AVSL) & (np.roll(close_prices, 1) >= np.roll(AVSL, 1))
        # Проверка наличия сигнала на последнем баре
        last_bar_signal = None
        if cross_up[-1]:
            last_bar_signal = 'cross_up'
        elif cross_down[-1]:
            last_bar_signal = 'cross_down'
        return cross_up, cross_down, AVSL, close_prices, last_bar_signal



"""
data = LoadDataFromYF.load_test_data("AAPL", start="2023-06-14", end="2024-02-14", timeframe="1h")
# Подготавливаем для расчета
cross_up, cross_down, AVSL, close_prices, last_bar_signal = AVSLIndicator.calculate_avsl(data)
AVSLIndicator.avsl_visualization(cross_up, cross_down, AVSL, close_prices, data)
print(last_bar_signal)
"""
