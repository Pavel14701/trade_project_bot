import pandas as pd
from pandas_ta import accbands
import numpy as np

from strategies.src.domain.entities import AcceletrationBandsDM
from strategies.src.infrastructure._types import PriceDataFrame


class AccelerationBands:
    """
    Acceleration Bands Indicator Implementation.

    Acceleration Bands (ACCB) were developed by Mark Helweg and 
    are designed to indicate volatility and acceleration in 
    price movements. These bands consist of an **upper band**, 
    **lower band**, and **centerline** derived from a 
    moving average.

    Formula:
    1. Compute a Moving Average (`mamode`) over the defined `length`.
    2. Calculate the **upper acceleration band**: MA * (1 + percentage factor).
    3. Calculate the **lower acceleration band**: MA * (1 - percentage factor).
    4. Identify **buy and sell signals** when prices interact with these bands.
    Usage:
    - Helps detect periods of **increasing or decreasing price acceleration**.
    - Can be used to identify **potential breakouts** when price breaches the bands.
    """

    def calc_accbands(
        self, 
        data: PriceDataFrame, 
        config: AcceletrationBandsDM
    ) -> pd.DataFrame:
        """
        Calculates Acceleration Bands (ACCB) values.
        Args:
            data (PriceDataFrame): Price dataset containing 
              high, low, and close prices.
            config (AcceletrationBandsDM): Configuration for 
              Acceleration Bands (length, smoothing 
              method, drift, offset).
        Returns:
            pd.DataFrame: A DataFrame containing upper, 
              lower, and center acceleration bands.
        """
        # Compute Acceleration Bands using pandas-ta
        if acc_bands := accbands(
            high=data.high_prices,
            low=data.low_prices,
            close=data.close_prices,
            length=config.length,
            drift=config.drift,
            mamode=config.mamode,
            offset=config.offset,
        ):
            # Align index with input data
            acc_bands.index = data.index  
            # Preserve close prices for signal generation
            acc_bands['close_prices'] = data.close_prices  
            return acc_bands
        # Raise an error if calculation fails
        raise ValueError("No data in DataFrame")

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generates trading signals based on Acceleration 
        Bands interaction.
        Signals:
        - **Buy:** Price crosses **above** the lower band.
        - **Sell:** Price crosses **below** the upper band.
        Args:
            data (pd.DataFrame): DataFrame containing 
            Acceleration Bands and price data.
        Returns:
            pd.DataFrame: A DataFrame containing buy/sell signals.
        """
        # Extract bands
        upper_band = data['ACCbands_upper'].values
        lower_band = data['ACCbands_lower'].values
        # Buy signal: Price crosses above lower band
        buy_signal = (
            data["close_prices"] < upper_band
        ) & (
            np.roll(data["close_prices"], 1) > upper_band
        )
        # Sell signal: Price crosses below upper band
        sell_signal = (
            data["close_prices"] > lower_band
        ) & (
            np.roll(data["close_prices"], 1) < lower_band
        )
        # Create a DataFrame to store signals
        signals = pd.DataFrame(index=data.index)
        signals['buy_signals'] = buy_signal.astype(int)
        signals['sell_signals'] = sell_signal.astype(int)
        return signals

    def check_last_signal(
        self, 
        data: PriceDataFrame, 
        config: AcceletrationBandsDM
    ) -> str | None:
        """
        Determines the last trading signal based on Acceleration Bands.
        - If the last bar has a buy signal → returns "long".
        - If the last bar has a sell signal → returns "short".
        - If no signal is detected → returns None.
        Args:
            data (PriceDataFrame): Market data with price information.
            config (AcceletrationBandsDM): Configuration for Acceleration Bands.
        Returns:
            str | None: "long" if buy signal, "short" if sell signal, 
            or None if no signal is present.
        """
        #  Compute Acceleration Bands values
        acc_bands_df = self.calc_accbands(data, config)
        # Generate buy/sell signals
        signals_df = self.generate_signals(acc_bands_df)
        # Determine the last signal based on recent price action
        if signals_df["Buy Signals"].iloc[-1] == 1:
            return "long"
        elif signals_df["Sell Signals"].iloc[-1] == 1:
            return "short"        
        return None
