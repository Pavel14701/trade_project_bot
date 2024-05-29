# Импортируем библиотеки
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

class Alma:
    def __init__(self, lenghts=None, instId, timeframe, test=None):
        self.lenghts = lenghts
        self.instId = instId
        self.timeframe = timeframe
        self.test = test
        
    def load_dest_data(ticker, start, end, timeframe):
        if self.test not None:
            # Загружаем данные по акциям Apple
            data = yf.download(ticker, start, end, interval=timeframe)
            return (test_data, ticker)
        else:
            pass
        
    def calculate(self):
        if self.test not None:
        # Вычисляем ALMA с длиной окна 20 и стандартными параметрами
        lenghts = self.lenghts
        m = (N - 1) / 2
        sigma = N / 6
        w = np.exp(-(np.arange(N) - m)**2 / (2 * sigma**2))
        w = w / w.sum()
        data["ALMA"] = data["Close"].rolling(N).apply(lambda x: np.dot(x, w), raw=True)
        return alma_data

    def create_vizualization(self, alma_data, ticker=None):
        if self.test not None:
            inst = ticker
        else:
            inst = self.instId
        # Строим график цены и ALMA
        plt.figure(figsize=(10, 6))
        plt.plot(data["Close"], label="Price")
        plt.plot(data["ALMA"], label="ALMA")
        plt.title(f"{inst} Stock Price with ALMA")
        plt.xlabel("Date")
        plt.ylabel("USDT")
        plt.legend()
        plt.show()
