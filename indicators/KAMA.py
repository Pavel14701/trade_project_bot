# Импортируем библиотеки
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from decimal import Decimal
import sys

# Загружаем данные
df = yf.download("BTC", start="2021-01-01", end="2024-02-14", interval="1D")

# Определяем функцию для расчета KAMA
def kama(df, period, fast, slow):
    # Вычисляем направление и волатильность
    direction = abs(((df['High'] - df['High'].shift(period)) + (df['Low'] - df['Low'].shift(period))) / 2)
    volatility = (df['High'].diff().abs().rolling(period).sum() + df['Low'].diff().abs().rolling(period).sum()) / 2 + 0.0001# добавим небольшое число к волатильности
    # Вычисляем коэффициент эффективности
    er = direction / volatility
    # Вычисляем сглаживающую константу
    sc = (er * (2 / (fast + 1) - 2 / (slow + 1)) + 2 / (slow + 1)) ** 2
    # Вычисляем KAMA
    kama = np.zeros(len(df))
    kama[period] = (df['High'][period] + df['Low'][period]) / 2 # используем среднее между high и low
    for i in range(period + 1, len(df)):
        kama[i] = kama[i-1] + sc[i] * ((df['High'][i] + df['Low'][i]) / 2 - kama[i-1]) # используем среднее между high и low и одну разность
    # Возвращаем результат
    return kama







# Выбираем период и скорости для KAMA
period = 54
fast = 3
slow = 34

# Добавляем колонку с KAMA в датафрейм
df['KAMA_H'] = kama(df, period, fast, slow)

# Строим график цены и KAMA
plt.figure(figsize=(12,8))
plt.plot(df['Close'], label='Price')
plt.plot(df['KAMA_H'], label='KAMA_H')
plt.title('Btc Price and KAMA')
plt.xlabel('Date')
plt.ylabel('USD')
plt.legend()
plt.show()
