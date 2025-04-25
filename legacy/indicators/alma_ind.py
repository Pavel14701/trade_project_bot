#libs
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame
#configs
from configs.load_settings import ConfigsProvider
#utils
from baselogs.custom_logger import create_logger
from baselogs.custom_decorators import log_exceptions, deprecated


class AlmaIndicator:
    def __init__(self, data:DataFrame):
        settings = ConfigsProvider().load_alma_configs()
        self.lenghtsVSlow = settings['lenghtsVSlow']
        self.lenghtsSlow = settings['lenghtsSlow']
        self.lenghtsMiddle = settings['lenghtsMiddle']
        self.lenghtsFast = settings['lenghtsFast']
        self.lenghtsVFast = settings['lenghtsVFast']
        self.lenghts = settings['lenghts']
        self.data = data


    def calculate_alma(self):
        if self.lenghts is None:
            raise NotImplementedError("lenghts param must be integer, watch alma env configs")
        close_prices = self.data['Close'].values.astype('float64')
        m = (self.lenghts - 1) / 2
        sigma = self.lenghts / 6
        w = np.exp(-(np.arange(self.lenghts) - m)**2 / (2 * sigma**2))
        w = w / w.sum()
        ALMA = self.data["Close"].rolling(self.lenghts).apply(lambda x: np.dot(x, w), raw=True)
        cross_up = (close_prices > ALMA) & (np.roll(close_prices, 1) <= np.roll(ALMA, 1))
        cross_down = (close_prices < ALMA) & (np.roll(close_prices, 1) >= np.roll(ALMA, 1))
        Price_Above_ALMA = (self.data["Close"] > self.data["ALMA"]).astype(int)
        Price_Below_ALMA = (self.data["Close"] < self.data["ALMA"]).astype(int)
        last_bar_signal = None
        if cross_up[-1]:
            last_bar_signal = 'cross_up'
        elif cross_down[-1]:
            last_bar_signal = 'cross_down'
        return (cross_up, cross_down, close_prices, last_bar_signal)

    

    @staticmethod
    def create_vizualization_alma_ribbon(data):
        plt.figure(figsize=(10, 6))
        plt.plot(data["Close"], label="Price")
        plt.plot(data["ALMA"], label="ALMA_SLOW")
        plt.title("Stock Price with ALMA")
        plt.xlabel("Date")
        plt.ylabel("USDT")
        plt.legend()
        plt.show()


    @deprecated
    def calculate_alma_ribbon(self):
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
    @deprecated
    def create_vizualization_alma_ribbon(data):
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

