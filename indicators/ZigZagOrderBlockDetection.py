import asyncio, pandas as pd, matplotlib.pyplot as plt, mplfinance as mpf
from concurrent.futures import ThreadPoolExecutor
from pandas_ta import zigzag
from User.LoadSettings import LoadUserSettingData
from utils.CustomLogger import create_logger
from utils.CustomDecorators import log_exceptions
logger = create_logger('ZigZagOrderBlockDetection')



from User.UserInfoFunctions import UserInfo
from utils.DataFrameUtils import prepare_many_data_to_append_db, create_dataframe


class ZigZagIndicator:
    def __init__(self, data: pd.DataFrame):
        settings = LoadUserSettingData.load_zigzag_configs()
        self.legs = settings['zigzag_legs']
        self.deviation = settings['zigzag_deviation']
        self.retrace = settings['zigzag_retrace']
        self.last_extreme = settings['zigzag_last_extreme']
        self.offset = settings['zigzag_offset']
        self.data = data


    @log_exceptions(logger)
    def calculate_zigzag(self) -> pd.DataFrame:
        if self.data[['High', 'Low', 'Close']].isnull().values.any():
            raise ValueError("There are missing values ​​(NaN) in the data.")
        zigzag_ind = zigzag(
            high=self.data['High'], low=self.data['Low'], close=None,
            legs=self.legs, deviation=self.deviation, retrace=self.retrace,
            last_extreme=self.last_extreme, offset=self.offset
        )
        self.data['zigzag'] = zigzag_ind[f'ZIGZAGv_{self.deviation}%_{self.legs}'].interpolate()
        if self.data['zigzag'].isnull().values.all():
            raise ValueError('The ZigZag result contains only NaN values. Check the settings and data.')
        print(self.data['zigzag'])
        return self.data


    async def calculate_zigzag_async(self) -> pd.DataFrame:
        executor = ThreadPoolExecutor()
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(executor, self.calculate_zigzag)
        return data


    def create_zigzag_vizualization(self) -> plt:
        self.calculate_zigzag()
        addplot = mpf.make_addplot(self.data['zigzag'], color='red')
        mpf.plot(self.data, type='candle', style='charles', addplot=addplot,\
            title='OHLC и ZigZag Индикатор', ylabel='Цена')
        plt.show()
