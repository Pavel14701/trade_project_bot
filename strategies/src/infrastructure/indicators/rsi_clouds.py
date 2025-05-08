import numpy as np
import pandas as pd
import pandas_ta as ta

from strategies.src.domain.entities import RsiCloudsConfigDM
from strategies.src.infrastructure._types import PriceDataFrame


class CloudsRsi:
    def prepare_data(self, data: PriceDataFrame) -> pd.Series:
        """Создание среднего ценового ряда."""
        return (
            data.low_prices + 
            data.high_price + 
            data.open_price + 
            data.close_prices
        ) / 4

    def calculate(
        self, 
        data: PriceDataFrame, 
        config: RsiCloudsConfigDM
    ) -> pd.DataFrame:
        """Расчет RSI и MACD."""
        ohlc = pd.DataFrame(
            data={"avg": self.prepare_data(data)}, 
            index=data.date
        )
        ohlc['rsi'] = ta.rsi(
            close=ohlc["avg"], 
            length=config.rsi_length, 
            scalar=config.scalar,
            drift=config.drift,
            offset=config.offset, 
            talib=config.talib, 
        )
        
        macd_ind = ta.macd(
            close=ohlc['rsi'],
            fast=config.macd_fast, 
            slow=config.macd_slow, 
            signal=config.macd_signal,
            talib=config.talib, 
            offset=config.offset
        )
        suffixes = {"": "macd_line", "s": "macd_signal", "h": "histogram"}
        ohlc = ohlc.join(macd_ind.rename(columns={
            f"MACD{suffix}_{config.macd_fast}_"
            f"{config.macd_slow}_{config.macd_signal}": name
            for suffix, name in suffixes.items()
        }))
        del macd_ind
        return ohlc

    def create_signals(self, ohlc: pd.DataFrame) -> pd.DataFrame:
        """Создание сигналов на основе пересечения MACD."""
        prev_macd_line = ohlc['macd_line'].shift(1)
        prev_macd_signal = ohlc['macd_signal'].shift(1)
        
        ohlc['macd_cross_signal'] = np.select(
            [
                (
                    prev_macd_line < prev_macd_signal
                ) & (
                    ohlc['macd_line'] > ohlc['macd_signal']
                ),
                (
                    prev_macd_line > prev_macd_signal
                ) & (
                    ohlc['macd_line'] < ohlc['macd_signal']
                ),
            ],
            [1, -1],
            default=0
        )
        ohlc['histogram_cross_zero'] = np.select(
            [
                (ohlc['histogram'].shift(1) < 0) & (ohlc['histogram'] > 0),
                (ohlc['histogram'].shift(1) > 0) & (ohlc['histogram'] < 0),
            ],
            [1, -1],
            default=0
        )
        return ohlc

    def get_last_signal(self, ohlc: pd.DataFrame) -> str:
        """Определяет последний сигнал MACD (без учета гистограммы)."""
        if ohlc.empty:
            return "None"
        last_macd_signal = ohlc['macd_cross_signal'].iloc[-1]
        if last_macd_signal == 1:
            return "Buy"
        elif last_macd_signal == -1:
            return "Sell"
        else:
            return "None"
