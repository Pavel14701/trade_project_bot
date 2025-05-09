import talib as ta
from pandas import DataFrame

from strategies.src.domain.entities import StochRsiConfigDM
from strategies.src.infrastructure._types import PriceDataFrame


class StochRSI:    
    def calculate_stochrsi(
        self, 
        data: PriceDataFrame,
        config: StochRsiConfigDM
    ) -> DataFrame:
        fastk, fastd = ta.STOCHRSI(
            close=data.close_prices, 
            timeperiod=config.timeperiod, 
            fastk_period=config.fastk_period, 
            fastd_period=config.fastd_period, 
            fastd_matype=config.fastd_matype
        )
        return DataFrame(
            {"fastk": fastk, "fastd": fastd}, 
            index=data.index
        )

    def create_signals(self, data: DataFrame) -> DataFrame:
        cross_up = (
            data['fastk'] > data['fastd']
        ) & (
            data['fastk'].shift(1) < data['fastd'].shift(1)
        ) & (
            data['fastk'] < 20
        )
        cross_down = (
            data['fastk'] < data['fastd']
        ) & (
            data['fastk'].shift(1) > data['fastd'].shift(1)
        ) & (
            data['fastk'] > 80
        )
        return DataFrame(
            {"cross_up": cross_up, "cross_down": cross_down},
            index = data.index
        )

    def get_last_signal(self, data: PriceDataFrame) -> str:
        stoch_rsi = self.calculate_stochrsi(data)
        signals = self.create_signals(stoch_rsi)
        last_bar_signal: str
        if signals['cross_up'].any() and signals['cross_up'].iloc[-1]:
            last_bar_signal = 'long'
        if signals['cross_down'].any() and signals['Cross_down'].iloc[-1]:
            last_bar_signal = 'short'
        return last_bar_signal