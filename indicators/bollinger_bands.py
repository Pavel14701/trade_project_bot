#libs
import sys, asyncio, matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from pandas import DataFrame
from pandas_ta import bbands
#configs
from configs.load_settings import ConfigsProvider


class BollindgerBands:
    def __init__ (self, data: DataFrame):
        settings = ConfigsProvider().load_bollinger_bands_settings()
        self.lenghts = settings['bb_lenghts']
        self.stdev = settings['bb_stdev']
        self.ddof = settings['bb_ddof']
        self.mamode = settings['bb_mamode']
        self.talib = settings['bb_talib']
        self.offset = settings['bb_offset']
        self.data = data


    def calculate_bands(self) -> DataFrame:
        high_low_average = (self.data['High'] + self.data['Low']) / 2
        bbands_ind = bbands(
            high_low_average, self.lenghts, self.stdev,self.ddof,
            self.mamode, self.talib, self.offset
        )
        self.data['Upper_Band'] = bbands_ind['BBU_20_2.0']
        self.data['Middle_Band'] = bbands_ind['BBM_20_2.0']
        self.data['Lower_Band'] = bbands_ind['BBL_20_2.0']
        return self.data


    async def calculate_bands_async(self) -> DataFrame:
        executor = ThreadPoolExecutor()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, self.calculate_bands)
            

    def create_vizualization_bb(self) -> plt:
        self.calculate_bands()
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.plot(self.data.index, self.data['Close'], label='Цена закрытия', color='blue')
        ax.plot(self.data.index, self.data['Upper_Band'], label='Верхняя полоса', color='red', linestyle='--')
        ax.plot(self.data.index, self.data['Middle_Band'], label='Средняя полоса', color='black', linestyle='-.')
        ax.plot(self.data.index, self.data['Lower_Band'], label='Нижняя полоса', color='green', linestyle='--')
        ax.fill_between(self.data.index, self.data['Upper_Band'], self.data['Lower_Band'], color='grey', alpha=0.1)
        ax.legend()
        ax.set_title('Визуализация полос Боллинджера')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Цена')
        plt.show()
