import numpy as np
import talib
import matplotlib.pyplot as plt
import pandas as pd
#from test_data_loading import LoadDataFromYF


class AVSLIndicator:
    # Функция для расчета stop-loss шага в зависимости от объема и минимальной цены
    @staticmethod
    def price_fun(VPC, VPR, VM, src):
        PriceV = np.zeros_like(VPC)  # Создаем массив нулей той же формы, что и VPC
        for i in range(len(VPC)):
            VPCI = VPC[i] * VPR[i] * VM[i]
            if np.isnan(VPCI):  # Проверяем, является ли VPCI NaN
                lenV = 0
            else:
                lenV = int(round(abs(VPCI - 3))) if VPC[i] < 0 else round(VPCI + 3)
            VPCc = -1 if (VPC[i] > -1 and VPC[i] < 0) else 1 if (VPC[i] < 1 and VPC[i] >= 0) else VPC[i]
            Price = np.sum(src[i-lenV+1:i+1] / VPCc / VPR[i-lenV+1:i+1]) if lenV > 0 else src[i]
            PriceV[i] = Price / lenV / 100 if lenV > 0 else Price
        return PriceV


    @staticmethod
    def prepare_calculate_avsl(data):
        # Подготовка данных
        close_prices = data['Adj Close'].values.astype('float64')
        low_prices = data['Low'].values.astype('float64')
        volumes = data['Volume'].values.astype('float64')
        # Параметры
        lenghtsFast = 34  # Быстрая скользящая средняя
        lenghtsSlow = 134  # Медленная скользящая средняя
        lenT = 9   # Сигнал для VPCI
        standDiv = 3.0 # Стандартное отклонение
        offset = 2 # Смещение
        # Расчеты
        VWmaS = talib.WMA(close_prices, timeperiod=lenghtsSlow)  # Медленная VWMA
        VWmaF = talib.WMA(close_prices, timeperiod=lenghtsFast)  # Быстрая VWMA
        AvgS = talib.SMA(close_prices, timeperiod=lenghtsSlow)   # Медленная средняя объема
        AvgF = talib.SMA(close_prices, timeperiod=lenghtsFast)   # Быстрая средняя объема
        VPC = VWmaS - AvgS                                # VPC+/-
        VPR = VWmaF / AvgF                                # Отношение цены к объему
        VM = talib.SMA(volumes, timeperiod=lenghtsFast) / talib.SMA(volumes, timeperiod=lenghtsSlow)  # Множитель объема
        VPCI = VPC * VPR * VM                             # Индикатор VPCI
        DeV = standDiv * VPCI * VM                            # Отклонение
        return(close_prices, DeV, low_prices, VPC, VPR, VM, lenghtsSlow)


    @staticmethod
    def calculate_avsl(data):
        if not isinstance(data, pd.DataFrame):
            print("Пошёл нахуй")
        else:
            close_prices, DeV, low_prices, VPC, VPR, VM, lenghtsSlow = AVSLIndicator.prepare_calculate_avsl(data)
            PriceV = AVSLIndicator.price_fun(VPC, VPR, VM, low_prices)
            AVSL = talib.SMA(low_prices - PriceV + DeV, timeperiod=lenghtsSlow)
            cross_up = (close_prices > AVSL) & (np.roll(close_prices, 1) <= np.roll(AVSL, 1))
            cross_down = (close_prices < AVSL) & (np.roll(close_prices, 1) >= np.roll(AVSL, 1))
            return(cross_up, cross_down, AVSL, close_prices)


    @staticmethod
    def avsl_visualization(cross_up, cross_down, AVSL, close_prices, data):
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.plot(data.index, close_prices, label='Цена закрытия', color='blue')
        ax.plot(data.index, AVSL, label='AVSL', color='orange')
        ax.scatter(data.index[cross_up], close_prices[cross_up], color='green', label='Пересечение вверх', marker='^', alpha=0.7)
        ax.scatter(data.index[cross_down], close_prices[cross_down], color='red', label='Пересечение вниз', marker='v', alpha=0.7)
        ax.legend()
        ax.set_title('Визуализация AVSL')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Цена')
        plt.show()


"""
a = LoadDataFromYF("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
data = a.load_test_data()
# Подготавливаем для расчета
cross_up, cross_down, AVSL, close_prices = AVSLIndicator.calculate_avsl(data)
AVSLIndicator.avsl_visualization(cross_up, cross_down, AVSL, close_prices, data)
"""
