import yfinance as yf
import numpy as np
import talib
import matplotlib.pyplot as plt

# Загрузка данных акций Apple
data = yf.download("AAPL", start="2023-01-01", end="2024-05-23", interval="1h")

# Подготовка данных
close_prices = data['Close'].values.astype('float64')
low_prices = data['Low'].values.astype('float64')
volumes = data['Volume'].values.astype('float64')

# Параметры
lenF = 34  # Быстрая скользящая средняя
lenS = 134  # Медленная скользящая средняя
lenT = 9   # Сигнал для VPCI
mult = 3.0 # Стандартное отклонение
offset = 2 # Смещение

# Функция для расчета stop-loss шага в зависимости от объема и минимальной цены
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

# Расчеты
VWmaS = talib.WMA(close_prices, timeperiod=lenS)  # Медленная VWMA
VWmaF = talib.WMA(close_prices, timeperiod=lenF)  # Быстрая VWMA
AvgS = talib.SMA(close_prices, timeperiod=lenS)   # Медленная средняя объема
AvgF = talib.SMA(close_prices, timeperiod=lenF)   # Быстрая средняя объема
VPC = VWmaS - AvgS                                # VPC+/-
VPR = VWmaF / AvgF                                # Отношение цены к объему
VM = talib.SMA(volumes, timeperiod=lenF) / talib.SMA(volumes, timeperiod=lenS)  # Множитель объема
VPCI = VPC * VPR * VM                             # Индикатор VPCI

DeV = mult * VPCI * VM                            # Отклонение
AVSL = talib.SMA(low_prices - price_fun(VPC, VPR, VM, low_prices) + DeV, timeperiod=lenS)


# Определение точек пересечения
cross_up = (close_prices > AVSL) & (np.roll(close_prices, 1) <= np.roll(AVSL, 1))
cross_down = (close_prices < AVSL) & (np.roll(close_prices, 1) >= np.roll(AVSL, 1))

# Отображение графика
plt.figure(figsize=(14, 7))
plt.plot(data.index, close_prices, label='Цена закрытия', color='blue')
plt.plot(data.index, AVSL, label='AVSL', color='red', linestyle='--')

# Сигналы на вход
plt.plot(data.index[cross_up], close_prices[cross_up], '^', markersize=10, color='g', lw=0, label='Сигнал на вход (покупка)')
plt.plot(data.index[cross_down], close_prices[cross_down], 'v', markersize=10, color='r', lw=0, label='Сигнал на вход (продажа)')

plt.title('График цены закрытия и AVSL с сигналами')
plt.xlabel('Дата')
plt.ylabel('Цена')
plt.legend()
plt.show()
