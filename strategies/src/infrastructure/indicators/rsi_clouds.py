import numpy as np
import pandas as pd
import pandas_ta as ta

from strategies.src.domain.entities import RsiCloudsConfigDM
from strategies.src.infrastructure._types import PriceDataFrame


class RsiClouds:
    """
    RSI Clouds Indicator Implementation.

    The RSI Clouds technique integrates 
      **Relative Strength Index (RSI)** and **MACD** 
      to provide momentum-based trend insights.

    Formula:
    1. Compute the **average price** using OHLC values.
    2. Calculate **RSI** based on the average price to track momentum.
    3. Apply **MACD** to RSI to highlight trend shifts.
    4. Generate trading signals based on:
       - **MACD line crossing its signal line** (entry/exit points).
       - **MACD histogram crossing zero** (trend confirmation).
    Usage:
    - Helps traders visualize **momentum clouds** around RSI.
    - Combines two powerful indicators (RSI + MACD) for enhanced signal accuracy.
    """

    def prepare_data(self, data: PriceDataFrame) -> pd.Series:
        """
        Creates the average price series from OHLC values.
        Args:
            data (PriceDataFrame): Market price dataset.
        Returns:
            pd.Series: A time series representing the 
              average price.
        """
        # Computes the mean price from open, high, low, and close.
        return (
            data.low_prices + 
            data.high_prices + 
            data.open_price + 
            data.close_prices
        ) / 4  

    def calculate_rsi_clouds(
        self, 
        data: PriceDataFrame, 
        config: RsiCloudsConfigDM
    ) -> pd.DataFrame:
        """
        Computes RSI and MACD based on the average price.
        Args:
            data (PriceDataFrame): Market price dataset.
            config (RsiCloudsConfigDM): RSI Clouds 
              configuration settings.
        Returns:
            pd.DataFrame: A DataFrame containing 
              RSI values and MACD indicators.
        """
        # Prepare average price data
        ohlc = pd.DataFrame(
            data={"avg": self.prepare_data(data)}, 
            index=data.date
        )
        # Compute RSI based on average price
        ohlc['rsi'] = ta.rsi(
            close=ohlc["avg"], 
            length=config.rsi_length, 
            scalar=config.scalar,
            drift=config.drift,
            offset=config.offset, 
            talib=config.talib
        )
        # Compute MACD based on RSI values
        macd_ind = ta.macd(
            close=ohlc['rsi'],
            fast=config.macd_fast, 
            slow=config.macd_slow, 
            signal=config.macd_signal,
            talib=config.talib, 
            offset=config.offset
        )
        # Rename MACD components for clarity
        suffixes = {"": "macd_line", "s": "macd_signal", "h": "histogram"}
        ohlc = ohlc.join(macd_ind.rename(columns={
            f"MACD{suffix}_{config.macd_fast}_"
            f"{config.macd_slow}_{config.macd_signal}": name
            for suffix, name in suffixes.items()
        }))
        # Free up memory
        del macd_ind  
        return ohlc

    def create_signals(self, ohlc: pd.DataFrame) -> pd.DataFrame:
        """
        Generates buy/sell signals based on MACD crossovers.
        Signals:
        - **Buy:** MACD crosses **above** the signal line.
        - **Sell:** MACD crosses **below** the signal line.
        - **Histogram crosses zero:** Confirms trend shift.
        Args:
            ohlc (pd.DataFrame): DataFrame 
              containing RSI and MACD values.
        Returns:
            pd.DataFrame: A DataFrame 
              with trading signals.
        """
        # Extract previous MACD values for crossover detection
        prev_macd_line = ohlc['macd_line'].shift(1)
        prev_macd_signal = ohlc['macd_signal'].shift(1)
        # Identify MACD signal line crossovers
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
            # 1 → Buy, -1 → Sell
            [1, -1],  
            default=0
        )
        # Identify histogram crossing zero
        ohlc['histogram_cross_zero'] = np.select(
            [
                (ohlc['histogram'].shift(1) < 0) & (ohlc['histogram'] > 0),
                (ohlc['histogram'].shift(1) > 0) & (ohlc['histogram'] < 0),
            ],
            # 1 → Uptrend confirmation, -1 → Downtrend confirmation
            [1, -1],  
            default=0
        )
        return ohlc

    def get_last_signal(self, ohlc: pd.DataFrame) -> str | None:
        """
        Retrieves the last MACD crossover signal.
        Args:
            ohlc (pd.DataFrame): DataFrame containing 
              RSI and MACD values.
        Returns:
            str | None: "buy" if MACD crossed above, "sell" if 
              MACD crossed below, or None if no signal.
        """
        # Ensure data is available
        if ohlc.empty:
            return None
        last_macd_signal = ohlc['macd_cross_signal'].iloc[-1]
        if last_macd_signal == 1:
            return "buy"
        elif last_macd_signal == -1:
            return "sell"
        else:
            return None
