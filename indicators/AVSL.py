#libs
import asyncio, pandas as pd, numpy as np, matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from pandas_ta import vwma, sma
#configs
from Configs.LoadSettings import LoadUserSettingData
#utils
from BaseLogs.CustomLogger import create_logger
from BaseLogs.CustomDecorators import log_exceptions


logger = create_logger('AVSL')

class AVSLIndicator:
    def __init__ (self, data: pd.DataFrame):
        settings = LoadUserSettingData().load_avsl_configs()
        self.lenghtsFast = settings['lenghtsFast']
        self.lenghtsSlow = settings['lenghtsSlow']
        self.lenT = settings['lenT']
        self.standDiv = settings['standDiv']
        self.offset = settings['offset']
        self.data = data


    @log_exceptions(logger)
    def calculate_avsl(self) -> pd.DataFrame:
        # Рассчитываем VWMA
        self.data['VWmaF'] = vwma(self.data['Close'], self.data['Volume'], length=self.lenghtsFast)
        self.data['VWmaS'] = vwma(self.data['Close'], self.data['Volume'], length=self.lenghtsSlow)
        # Рассчитываем VPC
        self.data['VPC'] = self.data['VWmaS'] - sma(self.data['Close'], lenght=self.lenghtsSlow, talib=True)
        # Рассчитываем VPR
        self.data['VPR'] = self.data['VWmaF'] / sma(self.data['Close'], lenght=self.lenghtsFast, talib=True)
        # Рассчитываем VM
        self.data['VM'] = sma(self.data['Volume'], length=self.lenghtsFast, talib=True) / sma(self.data['Volume'], length=self.lenghtsSlow, talib=True)
        self.data['VPCI'] = self.data['VPC'] * self.data['VPR'] * self.data['VM']
        PriceV = self.price_fun()
        DeV = self.standDiv * self.data['VPCI'] * self.data['VM']
        AVSL = sma(self.data['Low'] - PriceV + DeV, timeperiod=self.lenghtsSlow, talib=True)
        return self.data, AVSL


    @log_exceptions(logger)
    def price_fun(self):
        PriceV = np.zeros_like(self.data['VPC'])
        for i in range(len(self.data['VPC'])):
            if np.isnan(self.data['VPCI'].iloc[i]):
                lenV = 0
            else:
                lenV = int(round(abs(self.data['VPCI'].iloc[i] - 3))) if self.data['VPC'].iloc[i]\
                    < 0 else round(self.data['VPCI'].iloc[i] + 3)
            VPCc = -1 if (self.data['VPC'].iloc[i] > -1) & (self.data['VPC'].iloc[i] < 0) else 1 if\
                (self.data['VPC'].iloc[i] < 1) & (self.data['VPC'].iloc[i] >= 0) else self.data['VPC'].iloc[i]
            Price = np.sum(self.data['Low'].iloc[i - lenV + 1:i + 1] / VPCc / self.data['VPR'].iloc[i\
                - lenV + 1:i + 1]) if lenV > 0 else self.data['Low'].iloc[i]
            PriceV[i] = Price / lenV / 100 if lenV > 0 else Price
        (PriceV)
        return PriceV


    async def calculate_avsl_async(self) -> pd.DataFrame:
        executor = ThreadPoolExecutor()
        loop = asyncio.get_event_loop()
        data, avsl = await loop.run_in_executor(executor, self.calculate_avsl)
        return data, avsl


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