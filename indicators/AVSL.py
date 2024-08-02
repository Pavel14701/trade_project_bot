from User.LoadSettings import LoadUserSettingData
import pandas as pd
import pandas_ta as ta
import numpy as np
import matplotlib.pyplot as plt


class AVSLIndicator(LoadUserSettingData):
    def __init__ (self, data: pd.DataFrame):
        super().__init__()
        self.lenghtsFast = self.avsl_configs['lenghtsFast']
        self.lenghtsSlow = self.avsl_configs['lenghtsSlow']
        self.lenT = self.avsl_configs['lenT']
        self.standDiv = self.avsl_configs['standDiv']
        self.offset = self.avsl_configs['offset']
        self.data = data


    def calculate_avsl(self) -> pd.DataFrame:
        # Рассчитываем VWMA
        self.data['VWmaF'] = ta.vwma(self.data['Close'], self.data['Volume'], length=self.lenghtsFast)
        self.data['VWmaS'] = ta.vwma(self.data['Close'], self.data['Volume'], length=self.lenghtsSlow)
        # Рассчитываем VPC
        self.data['VPC'] = self.data['VWmaS'] - ta.sma(self.data['Close'], lenght=self.lenghtsSlow, talib=True)
        # Рассчитываем VPR
        self.data['VPR'] = self.data['VWmaF'] / ta.sma(self.data['Close'], lenght=self.lenghtsFast, talib=True)
        # Рассчитываем VM
        self.data['VM'] = ta.sma(self.data['Volume'], length=self.lenghtsFast, talib=True) / ta.sma(self.data['Volume'], length=self.lenghtsSlow, talib=True)
        self.data['VPCI'] = self.data['VPC'] * self.data['VPR'] * self.data['VM']
        PriceV, data = AVSLIndicator.price_fun(self.data)
        DeV = self.standDiv * data['VPCI'] * self.data['VM']
        AVSL = ta.sma(data['Low'] - PriceV + DeV, timeperiod=self.lenghtsSlow, talib=True)
        return data, AVSL
    
    @staticmethod
    def price_fun(data: pd.DataFrame):
        PriceV = np.zeros_like(data['VPC'])  # Создаем массив нулей той же формы, что и VPC
        for i in range(len(data['VPC'])):
            if np.isnan(data['VPCI'].iloc[i]):  # Проверяем, является ли VPCI NaN
                lenV = 0
            else:
                lenV = int(round(abs(data['VPCI'].iloc[i] - 3))) if data['VPC'].iloc[i] < 0 else round(data['VPCI'].iloc[i] + 3)
            VPCc = -1 if (data['VPC'].iloc[i] > -1) & (data['VPC'].iloc[i] < 0) else 1 if (data['VPC'].iloc[i] < 1) & (data['VPC'].iloc[i] >= 0) else data['VPC'].iloc[i]
            Price = np.sum(data['Low'].iloc[i - lenV + 1:i + 1] / VPCc / data['VPR'].iloc[i - lenV + 1:i + 1]) if lenV > 0 else data['Low'].iloc[i]
            PriceV[i] = Price / lenV / 100 if lenV > 0 else Price
        print(PriceV)
        return PriceV, data




    @staticmethod
    def create_avsl_vizualization(data:pd.DataFrame, AVSL) -> plt:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        ax1.plot(data.index, data['Close'], label='Цена закрытия', color='blue')
        ax1.plot(data.index, AVSL, label='AVSL', color='red')
        ax2.plot(data.index, data['VPCI'], label='VPCI', color='orange')
        ax1.legend()
        ax1.set_title('Визуализация VPCI')
        ax1.set_xlabel('Дата')
        ax1.set_ylabel('Цена')
        plt.show()