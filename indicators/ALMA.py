# Импортируем библиотеки
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# Загружаем данные по акциям Apple
data = yf.download("AAPL", start="2022-06-14", end="2024-02-14", interval="1h")

# Вычисляем ALMA с длиной окна 20 и стандартными параметрами
N = 233
m = (N - 1) / 2
sigma = N / 6
w = np.exp(-(np.arange(N) - m)**2 / (2 * sigma**2))
w = w / w.sum()
data["ALMA"] = data["Close"].rolling(N).apply(lambda x: np.dot(x, w), raw=True)

# Строим график цены и ALMA
plt.figure(figsize=(10, 6))
plt.plot(data["Close"], label="Price")
plt.plot(data["ALMA"], label="ALMA")
plt.title("Apple Stock Price with ALMA")
plt.xlabel("Date")
plt.ylabel("USD")
plt.legend()
plt.show()
