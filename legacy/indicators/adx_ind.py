#libs
import asyncio
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt, pandas as pd
from typing import Optional
from pandas_ta import adx
#configs
from configs.load_settings import ConfigsProvider


class ADXTrend:
    def __init__(self, data:pd.DataFrame, return_pd:Optional[bool]=None):
        settings = ConfigsProvider().load_adx_configs()
        self.timeperiod = settings['adx_timeperiod']
        self.lenghts_sig = settings['adx_lenghts_sig']
        self.adxr_lenghts = settings['adx_adxr_lenghts']
        self.adx_scalar = settings['adx_scalar']
        self.talib = settings['adx_talib']
        self.tvmode = settings['adx_tvmode']
        self.mamode = settings['adx_mamode']
        self.drift = settings['adx_drift']
        self.offset = settings['adx_offset']
        self.data = data
        self.return_pd = return_pd


    def _calculate_adx_sync(self) -> pd.DataFrame:
        adx_ind = adx(
            self.data['High'], self.data['Low'], self.data['Close'], 
            self.timeperiod, self.lenghts_sig, self.adxr_lenghts, self.adx_scalar,
            self.talib, self.tvmode, self.mamode, self.drift, self.offset
        )
        self.data['ADX'] = adx_ind[f'ADX_{self.timeperiod}']
        return self.data if self.return_pd else self.data['ADX'].iloc[-1]


    async def calculate_adx_async(self) -> pd.DataFrame:
        # sourcery skip: inline-immediately-returned-variable
        executor = ThreadPoolExecutor()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, self._calculate_adx_sync)
        return result


    def create_vizualization_adx(self):
        data = self._calculate_adx_sync()
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        ax1.plot(data.index, data['Close'], label='Цена закрытия', color='blue')
        ax2.plot(data.index, data['ADX'], label='ADX', color='orange')
        ax1.legend()
        ax1.set_title('Визуализация ADX')
        ax1.set_xlabel('Дата')
        ax1.set_ylabel('Цена')
        plt.show()