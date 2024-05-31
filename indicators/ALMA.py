import numpy as np
import matplotlib.pyplot as plt
#from test_data_loading import LoadDataFromYF


class AlmaIndicator:
    @staticmethod
    def calculate_alma(data, lenghts):
        # Вычисляем ALMA с длиной окна 20 и стандартными параметрами
        m = (lenghts - 1) / 2
        sigma = lenghts / 6
        w = np.exp(-(np.arange(lenghts) - m)**2 / (2 * sigma**2))
        w = w / w.sum()
        data["ALMA"] = data["Close"].rolling(lenghts).apply(lambda x: np.dot(x, w), raw=True)
        return data
    

    @staticmethod
    def create_vizualization_alma_ribbon(data):
        # Строим график цены и ALMA
        plt.figure(figsize=(10, 6))
        plt.plot(data["Close"], label="Price")
        plt.plot(data["ALMA"], label="ALMA_SLOW")
        plt.title("Stock Price with ALMA")
        plt.xlabel("Date")
        plt.ylabel("USDT")
        plt.legend()
        plt.show()


    @staticmethod
    def calculate_alma_ribbon(data, lenghtsVSlow, lenghtsSlow, lenghtsMiddle, lenghtsFast, lenghtsVFast):
        # Вычисляем ALMA с длиной окна 20 и стандартными параметрами
        m = (lenghtsVSlow - 1) / 2
        sigma = lenghtsVSlow / 6
        w = np.exp(-(np.arange(lenghtsVSlow) - m)**2 / (2 * sigma**2))
        w = w / w.sum()
        data["ALMA_VSLOW"] = data["Close"].rolling(lenghtsVSlow).apply(lambda x: np.dot(x, w), raw=True)
        m = (lenghtsSlow - 1) / 2
        sigma = lenghtsSlow / 6
        w = np.exp(-(np.arange(lenghtsSlow) - m)**2 / (2 * sigma**2))
        w = w / w.sum()
        data["ALMA_SLOW"] = data["Close"].rolling(lenghtsSlow).apply(lambda x: np.dot(x, w), raw=True)
        m = (lenghtsMiddle - 1) / 2
        sigma = lenghtsMiddle / 6
        w = np.exp(-(np.arange(lenghtsMiddle) - m)**2 / (2 * sigma**2))
        w = w / w.sum()
        data["ALMA_MIDDLE"] = data["Close"].rolling(lenghtsMiddle).apply(lambda x: np.dot(x, w), raw=True)
        m = (lenghtsFast - 1) / 2
        sigma = lenghtsFast / 6
        w = np.exp(-(np.arange(lenghtsFast) - m)**2 / (2 * sigma**2))
        w = w / w.sum()
        data["ALMA_FAST"] = data["Close"].rolling(lenghtsFast).apply(lambda x: np.dot(x, w), raw=True)
        m = (lenghtsVFast - 1) / 2
        sigma = lenghtsVFast / 6
        w = np.exp(-(np.arange(lenghtsVFast) - m)**2 / (2 * sigma**2))
        w = w / w.sum()
        data["ALMA_VFAST"] = data["Close"].rolling(lenghtsVFast).apply(lambda x: np.dot(x, w), raw=True)
        return data


    @staticmethod
    def create_vizualization_alma_ribbon(data):
        # Строим график цены и ALMA
        plt.figure(figsize=(10, 6))
        plt.plot(data["Close"], label="Price")
        plt.plot(data["ALMA_VSLOW"], label="ALMA_VSLOW")
        plt.plot(data["ALMA_SLOW"], label="ALMA_SLOW")
        plt.plot(data["ALMA_MIDDLE"], label="ALMA_MIDDLE")
        plt.plot(data["ALMA_FAST"], label="ALMA_FAST")
        plt.plot(data["ALMA_VFAST"], label="ALMA_VFAST")
        plt.title("Stock Price with ALMA")
        plt.xlabel("Date")
        plt.ylabel("USDT")
        plt.legend()
        plt.show()
        
""""
#пример применения
data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
print(data)
data = AlmaIndicator.calculate_alma_ribbon(data, lenghtsVSlow=144, lenghtsSlow=89, lenghtsMiddle=55, lenghtsFast=34, lenghtsVFast=21)
AlmaIndicator.create_vizualization_alma_ribbon(data)
"""
