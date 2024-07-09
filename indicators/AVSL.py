import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
import numpy as np
import talib
import matplotlib.pyplot as plt
import pandas as pd
from User.LoadSettings import LoadUserSettingData


class AVSLIndicator(LoadUserSettingData):
    def __init__ (self, data: pd.DataFrame):
        super().__init__()
        self.lenghtsFast = self.avsl_configs['lenghtsFast']
        self.lenghtsSlow = self.avsl_configs['lenghtsSlow']
        self.lenT = self.avsl_configs['lenT']
        self.standDiv = self.avsl_configs['standDiv']
        self.offset = self.avsl_configs['offset']
        self.data = data
    
    @staticmethod
    def price_fun(VPC, VPR, VM, src):
        PriceV = np.zeros_like(VPC)
        for i in range(len(VPC)):
            VPCI = VPC[i] * VPR[i] * VM[i]
            if np.isnan(VPCI):
                lenV = 0
            else:
                lenV = int(round(abs(VPCI - 3))) if VPC[i] < 0 else round(VPCI + 3)
            VPCc = -1 if (VPC[i] > -1 and VPC[i] < 0) else 1 if (VPC[i] < 1 and VPC[i] >= 0) else VPC[i]
            Price = np.sum(src[i-lenV+1:i+1] / VPCc / VPR[i-lenV+1:i+1]) if lenV > 0 else src[i]
            PriceV[i] = Price / lenV / 100 if lenV > 0 else Price
        return PriceV


    def prepare_calculate_avsl(self):
        # Подготовка данных
        close_prices = self.data['Close'].values.astype('float64')
        low_prices = self.data['Low'].values.astype('float64')
        volumes = self.data['Volume'].values.astype('float64')
        # Расчеты
        VWmaS = talib.WMA(close_prices, timeperiod=self.lenghtsSlow)  # Медленная VWMA
        VWmaF = talib.WMA(close_prices, timeperiod=self.lenghtsFast)  # Быстрая VWMA
        AvgS = talib.SMA(close_prices, timeperiod=self.lenghtsSlow)   # Медленная средняя объема
        AvgF = talib.SMA(close_prices, timeperiod=self.lenghtsFast)   # Быстрая средняя объема
        VPC = VWmaS - AvgS                                # VPC+/-
        VPR = VWmaF / AvgF                                # Отношение цены к объему
        VM = talib.SMA(volumes, timeperiod=self.lenghtsFast) / talib.SMA(volumes, timeperiod=self.lenghtsSlow)  # Множитель объема
        VPCI = VPC * VPR * VM                             # Индикатор VPCI
        DeV = self.standDiv * VPCI * VM                            # Отклонение
        return (close_prices, DeV, low_prices, VPC, VPR, VM)


    def calculate_avsl(self):
        close_prices, DeV, low_prices, VPC, VPR, VM = AVSLIndicator.prepare_calculate_avsl(self)
        PriceV = AVSLIndicator.price_fun(VPC, VPR, VM, low_prices)
        AVSL = talib.SMA(low_prices - PriceV + DeV, timeperiod=self.lenghtsSlow)
        self.data['cross_up'] = (close_prices > AVSL) & (np.roll(close_prices, 1) <= np.roll(AVSL, 1))
        self.data['cross_down'] = (close_prices < AVSL) & (np.roll(close_prices, 1) >= np.roll(AVSL, 1))
        last_bar_signal = None
        if self.data['cross_up'][-1]:
            last_bar_signal = 'cross_up'
        elif self.data['cross_down'][-1]:
            last_bar_signal = 'cross_down'
        print(self.data)
        return {'last': AVSL[-1], 'data': self.data,'last_bar_signal': last_bar_signal}


    @staticmethod
    def avsl_visualization(cross_up, cross_down, AVSL, close_prices, data):
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.plot(data.index, close_prices, label='Цена закрытия', color='blue')
        ax.plot(data.index, AVSL, label='AVSL', color='orange')
        ax.scatter(data.index[cross_up], close_prices[cross_up], color='green', label='Пересечение вверх', marker='^', alpha=0.7)
        ax.scatter(data.index[cross_down], close_prices[cross_down], color='red', label='Пересечение вниз', marker='v', alpha=0.7)
        ax.legend()
        ax.set_title('Визуализация AVSL')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Цена')
        plt.show()

