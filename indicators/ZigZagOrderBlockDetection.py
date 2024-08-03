import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import mplfinance as mpf
from User.LoadSettings import LoadUserSettingData
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


    def calculate_zigzag(self) -> pd.DataFrame:
        if self.data[['High', 'Low', 'Close']].isnull().values.any():
            raise ValueError("There are missing values ​​(NaN) in the data.")
        zigzag = ta.zigzag(
            high=self.data['High'], low=self.data['Low'], close=None,
            legs=self.legs, deviation=self.deviation, retrace=self.retrace,
            last_extreme=self.last_extreme, offset=self.offset
        )
        self.data['zigzag'] = zigzag[f'ZIGZAGv_{self.deviation}%_{self.legs}'].interpolate()
        if self.data['zigzag'].isnull().values.all():
            raise ValueError('The ZigZag result contains only NaN values. Check the settings and data.')
        print(self.data['zigzag'])
        return self.data


    def create_zigzag_vizualization(self) -> plt:
        self.calculate_zigzag()
        addplot = mpf.make_addplot(self.data['zigzag'], color='red')
        mpf.plot(self.data, type='candle', style='charles', addplot=addplot, title='OHLC и ZigZag Индикатор', ylabel='Цена')
        plt.show()
