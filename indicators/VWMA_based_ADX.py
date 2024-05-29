# Импортируем библиотеки
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# Загружаем данные по акциям Apple
data = yf.download("AAPL", start="2023-01-01", end="2024-02-14", interval="1h")



# Вычисляем +DI и -DI с периодом 14
DI_Period = 14
data["UpMove"] = data["High"].diff()
data["DownMove"] = data["Low"].diff()
data["+DM"] = np.where((data["UpMove"] > data["DownMove"]) & (data["UpMove"] > 0), data["UpMove"], 0)
data["-DM"] = np.where((data["DownMove"] > data["UpMove"]) & (data["DownMove"] > 0), data["DownMove"], 0)
data["+DM_Smooth"] = data["+DM"].ewm(span=DI_Period, adjust=False).mean()
data["-DM_Smooth"] = data["-DM"].ewm(span=DI_Period, adjust=False).mean()
data["ATR"] = data["Close"].diff().abs().ewm(span=DI_Period, adjust=False).mean()
data["+DI"] = data["+DM_Smooth"] / data["ATR"] * 100
data["-DI"] = data["-DM_Smooth"] / data["ATR"] * 100
# Вычисляем ADX с периодом 14, порогом 25 и сглаживанием
ADX_Period = 14
ADX_Threshold = 25
ADX_Smooth = 2
data["DX"] = np.abs(data["+DI"] - data["-DI"]) / (data["+DI"] + data["-DI"]) * 100
data["ADX"] = data["DX"].ewm(span=ADX_Period, adjust=False).mean()
data["ADX_Smooth"] = data["ADX"].ewm(span=ADX_Smooth, adjust=False).mean()
# Находим локальные максимумы и минимумы линии ADX
data["ADX_Peak"] = data["ADX_Smooth"].where((data["ADX_Smooth"].shift(1) < data["ADX_Smooth"]) & (data["ADX_Smooth"].shift(-1) < data["ADX_Smooth"])).ffill(limit=1)
data["ADX_Trough"] = data["ADX_Smooth"].where((data["ADX_Smooth"].shift(1) > data["ADX_Smooth"]) & (data["ADX_Smooth"].shift(-1) > data["ADX_Smooth"])).ffill(limit=1)
# Соединяем эти точки с помощью линии тренда ADX
data["ADX_Trend"] = np.nan
data.loc[data["ADX_Peak"].notna(), "ADX_Trend"] = data["ADX_Peak"]
data.loc[data["ADX_Trough"].notna(), "ADX_Trend"] = data["ADX_Trough"]
data["ADX_Trend"] = data["ADX_Trend"].interpolate(method="linear")



# Создаем пустой список для хранения значений WMAV
WMAV = []
# Задаем период скользящей средней
n = 20
# Проходим по данным с шагом 1 час, начиная с n-го часа
for i in range(n, len(data)):
    # Выбираем данные за последние n часов
    data_n = data.iloc[i-n:i]
    # Вычисляем числитель и знаменатель формулы WMAV
    numerator = (data_n["Volume"] * data_n["Close"] * data_n["ADX_Trend"]).sum()
    denominator = (data_n["Volume"] * data_n["ADX_Trend"]).sum()
    # Вычисляем значение WMAV и добавляем его в список
    WMAV.append(numerator / (denominator + 1e-9))
# Добавляем значения WMAV в исходный датафрейм
data["WMAV"] = np.nan
data.loc[data.index[n:], "WMAV"] = WMAV


# Строим график цены, WMAV и линии тренда ADX
plt.figure(figsize=(10, 6))
plt.plot(data["Close"], label="Price")
plt.plot(data["WMAV"], label="WMAV")
plt.title("Apple Stock Price with WMAV and ADX Trendline")
plt.xlabel("Date")
plt.ylabel("USD")
plt.legend()
plt.show()
