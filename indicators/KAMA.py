import numpy as np
import matplotlib.pyplot as plt
#from test_data_loading import LoadDataFromYF


class KAMA:
    @staticmethod
    def kama(data, period, fast, slow):
        # Вычисляем направление и волатильность
        direction = abs(((data['High'] - data['High'].shift(period)) + (data['Low'] - data['Low'].shift(period))) / 2)
        volatility = (data['High'].diff().abs().rolling(period).sum() + data['Low'].diff().abs().rolling(period).sum()) / 2 + 0.0001 # добавим небольшое число к волатильности
        # Вычисляем коэффициент эффективности
        er = direction / volatility
        # Вычисляем сглаживающую константу
        sc = (er * (2 / (fast + 1) - 2 / (slow + 1)) + 2 / (slow + 1)) ** 2
        # Вычисляем KAMA
        kama = np.zeros(len(data))
        kama[period] = (data['High'].iloc[period] + data['Low'].iloc[period]) / 2 # используем среднее между high и low
        for i in range(period + 1, len(data)):
            kama[i] = kama[i-1] + sc.iloc[i] * ((data['High'].iloc[i] + data['Low'].iloc[i]) / 2 - kama[i-1]) # используем .iloc[] для sc
        return kama


    @staticmethod
    def calculate_kama(data, period, fast, slow):
        """
        Значения по умолчанию
        period = 54
        fast = 3
        slow = 34
        """
        # Добавляем колонку с KAMA в датафрейм
        data['KAMA_H'] = KAMA.kama(data, period, fast, slow)
        return data
    

    @staticmethod
    def create_visualization_kama(data):
        # Строим график цены и KAMA
        plt.figure(figsize=(12,8))
        plt.plot(data['Close'], label='Price')
        plt.plot(data['KAMA_H'], label='KAMA_H')
        plt.title('Btc Price and KAMA')
        plt.xlabel('Date')
        plt.ylabel('USD')
        plt.legend()
        plt.show()


"""
#Пример использования
data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
print(data)
data = KAMA.calculate_kama(data, period = 54, fast = 3, slow = 34)
KAMA.create_visualization_kama(data)
"""