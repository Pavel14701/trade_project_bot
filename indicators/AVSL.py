import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt




# Загрузка данных акций Apple с интервалом в 1 час
df = yf.download("AAPL", start="2023-01-01", end="2024-05-23", interval="1h")

# Убедимся, что столбец 'Low' содержит числовые значения
df['Low'] = df['Low'].astype(float)

def ema(data, length):
    return data.ewm(span=length, adjust=False).mean()

def sma(data, length):
    return data.rolling(window=length).mean()

def price_fun(vpc, vpr, vm, src):
    # Вычисляем Volume-Price Confirmation Indicator (VPCI)
    vpci = vpc * vpr * vm
    
    # Заменяем 'inf' и '-inf' на NaN
    vpci.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # Заполняем NaN нулями
    vpci.fillna(0, inplace=True)
    
    # Вычисляем len_v для каждого элемента, используя векторизованные операции
    len_v_series = vpci + 3
    len_v_series[vpc < 0] = (abs(vpci - 3)).round().astype(int)
    
    # Вычисляем среднюю цену на основе VPCI
    price_v_series = len_v_series.apply(lambda len_v: sum(src.iloc[i] for i in range(int(len_v))) / len_v if len_v > 0 else 0)
    return price_v_series

# Настройки
len_f = 12
len_s = 26
len_t = 9
mult = 2.0
offset = 2  # Этот параметр может быть использован для смещения индикатора на графике

# Расчеты
vwma_s = (df['Close'] * df['Volume']).rolling(window=len_s).sum() / df['Volume'].rolling(window=len_s).sum()
vwma_f = (df['Close'] * df['Volume']).rolling(window=len_f).sum() / df['Volume'].rolling(window=len_f).sum()
avg_s = sma(df['Close'], len_s)
avg_f = sma(df['Close'], len_f)
vpc = vwma_s - avg_s
vpr = vwma_f / avg_f
vm = sma(df['Volume'], len_f) / sma(df['Volume'], len_s)
vpci = vpc * vpr * vm
dev = mult * vpci * vm

# Теперь применяем функцию price_fun к Series
price_difference = price_fun(vpc, vpr, vm, df['Low'])

# Если price_fun возвращает числа, то не нужно использовать .dt.days
# В этом случае просто используйте результат напрямую
avsl = sma(df['Low'] - price_difference + dev, len_s)

# Добавляем результаты в DataFrame
df['AVSL'] = avsl.shift(-offset)  # Смещаем на заданное количество баров, если необходимо
print(df['AVSL'])
# Теперь df['AVSL'] содержит значения AVSL, которые вы можете использовать для анализа или отображения на графике
# Построение графика цены закрытия актива
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['Close'], label='Цена закрытия', color='blue')

# Создание вторичной оси Y для индикатора AVSL
ax2 = plt.twinx()
ax2.plot(df.index, df['AVSL'], label='AVSL', color='orange', linestyle='--')

# Настройка заголовка и легенды
plt.title('График цены закрытия и индикатора AVSL для AAPL')
plt.legend()

# Отображение графика
plt.show()

