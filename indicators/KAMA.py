import asyncio, pandas as pd, matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from pandas_ta import kama
from User.LoadSettings import LoadUserSettingData
from utils.CustomLogger import create_logger
from utils.CustomDecorators import log_exceptions
logger = create_logger('KAMA')


class KAMAIndicator:
    def __init__(self, data:pd.DataFrame):
        settings = LoadUserSettingData.load_kama_configs()
        self.lengths = settings['kama_lengths']
        self.fast = settings['kama_fast']
        self.slow = settings['kama_slow']
        self.drift = settings['kama_drift']
        self.offset = settings['kama_offset']
        self.data = data


    @log_exceptions(logger)
    def calculate_kama(self) -> pd.DataFrame:
        self.data['HL'] = (self.data['High'] + self.data['Low']) / 2
        self.data['KAMA'] = kama(
            self.data['HL'], length=self.lengths, fast=self.fast,
            slow=self.slow, drift=self.drift, offset=self.offset
        )
        return self.data


    async def calculate_kama_async(self) -> pd.DataFrame:
        executor = ThreadPoolExecutor()
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(executor, self.calculate_kama)
        return data


    def create_visualization_kama(self) -> plt:
        self.data = self.calculate_kama()
        plt.figure(figsize=(12,8))
        plt.plot(self.data['Close'], label='Price')
        plt.plot(self.data['KAMA'], label='KAMA')
        plt.title('Price and KAMA')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.show()