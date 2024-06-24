import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame
import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from User.LoadSettings import LoadUserSettingData
#from test_data_loading import LoadDataFromYF


class AlmaIndicator(LoadUserSettingData):
    def __init__(self, data:DataFrame):
        super().__init__()
        self.data = data
        self.lenghtsVSlow = self.alma_configs['lenghtsVSlow']
        self.lenghtsSlow = self.alma_configs['lenghtsSlow']
        self.lenghtsMiddle = self.alma_configs['lenghtsMiddle']
        self.lenghtsFast = self.alma_configs['lenghtsFast']
        self.lenghtsVFast = self.alma_configs['lenghtsVFast']
        self.lenghts = self.alma_configs['lenghts']

    
    def calculate_alma(self):
        if self.lenghts is None:
            raise NotImplementedError("lenghts param must be integer, watch alma env configs")
        # Вычисляем ALMA с длиной окна 20 и стандартными параметрами
        m = (self.lenghts - 1) / 2
        sigma = self.lenghts / 6
        w = np.exp(-(np.arange(self.lenghts) - m)**2 / (2 * sigma**2))
        w = w / w.sum()
        self.data["ALMA"] = self.data["Close"].rolling(self.lenghts).apply(lambda x: np.dot(x, w), raw=True)
        return self.data
    

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


    def calculate_alma_ribbon(self):
        # Вычисляем ALMA с длиной окна 20 и стандартными параметрами
        m = (self.lenghtsVSlow - 1) / 2
        sigma = self.lenghtsVSlow / 6
        w = np.exp(-(np.arange(self.lenghtsVSlow) - m)**2 / (2 * sigma**2))
        w = w / w.sum()
        self.data["ALMA_VSLOW"] = self.data["Close"].rolling(self.lenghtsVSlow).apply(lambda x: np.dot(x, w), raw=True)
        m = (self.lenghtsSlow - 1) / 2
        sigma = self.lenghtsSlow / 6
        w = np.exp(-(np.arange(self.lenghtsSlow) - m)**2 / (2 * sigma**2))
        w = w / w.sum()
        self.data["ALMA_SLOW"] = self.data["Close"].rolling(self.lenghtsSlow).apply(lambda x: np.dot(x, w), raw=True)
        m = (self.lenghtsMiddle - 1) / 2
        sigma = self.lenghtsMiddle / 6
        w = np.exp(-(np.arange(self.lenghtsMiddle) - m)**2 / (2 * sigma**2))
        w = w / w.sum()
        self.data["ALMA_MIDDLE"] = self.data["Close"].rolling(self.lenghtsMiddle).apply(lambda x: np.dot(x, w), raw=True)
        m = (self.lenghtsFast - 1) / 2
        sigma = self.lenghtsFast / 6
        w = np.exp(-(np.arange(self.lenghtsFast) - m)**2 / (2 * sigma**2))
        w = w / w.sum()
        self.data["ALMA_FAST"] = self.data["Close"].rolling(self.lenghtsFast).apply(lambda x: np.dot(x, w), raw=True)
        m = (self.lenghtsVFast - 1) / 2
        sigma = self.lenghtsVFast / 6
        w = np.exp(-(np.arange(self.lenghtsVFast) - m)**2 / (2 * sigma**2))
        w = w / w.sum()
        self.data["ALMA_VFAST"] = self.data["Close"].rolling(self.lenghtsVFast).apply(lambda x: np.dot(x, w), raw=True)
        return self.data


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
