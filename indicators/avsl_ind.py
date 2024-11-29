#libs
import asyncio, pandas as pd, numpy as np, matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from pandas_ta import vwma, sma
from typing import Optional
#configs
from configs.load_settings import ConfigsProvider



from datasets.database import DataAllDatasets
from datasets.tables import create_tables
from datasets.utils.dataframe_utils import prepare_many_data_to_append_db, create_dataframe



class AVSLIndicator:
    def __init__ (self, data: pd.DataFrame, return_pd:Optional[bool]=None):
        settings = ConfigsProvider().load_avsl_configs()
        self.lenghtsFast = settings['lenghtsFast']
        self.lenghtsSlow = settings['lenghtsSlow']
        self.lenT = settings['lenT']
        self.standDiv = settings['standDiv']
        self.offset = settings['offset']
        self.data = data
        self.return_pd = return_pd


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
        PriceV = self.__price_fun()
        print(PriceV)
        DeV = self.standDiv * self.data['VPCI'] * self.data['VM']
        print(DeV)
        avsl = sma(self.data['Low'] - PriceV + DeV, timeperiod=self.lenghtsSlow, talib=True)
        print(avsl)
        return avsl if self.return_pd else self.data['avsl'].iloc[-1]


    def __price_fun(self):
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
        # sourcery skip: inline-immediately-returned-variable
        executor = ThreadPoolExecutor()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, self.calculate_avsl)
        return result


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

"""
async def main():
    instance_db = DataAllDatasetsAsync('BTC-USDT-SWAP', '1D')
    data = await instance_db.get_all_bd_marketdata_async()
    print(data)
    df = await create_dataframe_async(data)
    print(df)
    instance_ind = AVSLIndicator(df)
    data, avsl = await instance_ind.calculate_avsl_async()
    print(avsl)

if __name__ == '__main__':
    asyncio.run(main())
"""
instId = 'BTC-USD'
timeframe = '1h'
test = True
Session, classes_dict = create_tables(test, instId, timeframe)
data = DataAllDatasets(Session, classes_dict, instId, timeframe, test).get_all_bd_marketdata()
df = create_dataframe(data)
print(df)
a = AVSLIndicator(df, True)
ret =a.calculate_avsl()
print(ret)
