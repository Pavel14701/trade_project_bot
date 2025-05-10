import pandas as pd
from pandas_ta import accbands
import numpy as np

from strategies.src.domain.entities import AcceletrationBandsDM
from strategies.src.infrastructure._types import PriceDataFrame


class AccelerationBands:
    def calc_accbands(self, data: PriceDataFrame, config: AcceletrationBandsDM) -> pd.DataFrame:
        if acc_bands := accbands(
            high=data.high_prices,
            low=data.low_prices,
            close=data.close_prices,
            length=config.length,
            drift=config.drift,
            mamode=config.mamode,
            offset=config.offset,
        ):
            acc_bands.index = data.index
            acc_bands['close_prices'] = data.close_prices
            return acc_bands
        raise ValueError("No data in DataFrame")

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        upper_band = data['ACCbands_upper'].values
        lower_band = data['ACCbands_lower'].values
        buy_signal = (
            data["close_prices"] < upper_band
        ) & (
            np.roll(data["close_prices"], 1) > upper_band
        )
        sell_signal = (
            data["close_prices"] > lower_band
        ) & (
            np.roll(data["close_prices"], 1) < lower_band
        )
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = np.where(
            buy_signal, 
            'long', 
            np.where(
                sell_signal, 
                'short', 
                'neutral')
        )
        return signals

    def check_last_signal(self, data: PriceDataFrame, config) -> str:
        acc_bands = self.calc_accbands(data, config)
        signals = self.generate_signals(acc_bands)
        return signals['signal'].iloc[-1]
