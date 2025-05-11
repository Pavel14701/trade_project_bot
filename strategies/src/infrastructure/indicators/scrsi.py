import pandas as pd
import numpy as np

from strategies.src.domain.entities import ScrsiConfigDM
from strategies.src.infrastructure._types import PriceDataFrame


class SmoothCicleRsi:
    """
    SmoothCicle RSI (SCRSI) Indicator Implementation.

    This indicator calculates an adaptive RSI that includes 
    smoothing techniques to filter noise.
    It measures price momentum based on the 
    difference between closing prices over a 
    set cycle length.

    Formula:
    1. Calculate price difference (`diff = close_prices.diff()`).
    2. Compute the average of positive and negative movements:
       - up = average gain over `cyclelen` periods.
       - down = average loss over `cyclelen` periods.
    3. Standard RSI formula: RSI = 100 - (100 / (1 + up/down)).
    4. Convert RSI from range [0,100] to [-100,100] to highlight trends.
    5. Apply cyclic smoothing to refine RSI momentum shifts.
    6. Define boundaries (`Lower Bound` and `Upper Bound`)
       based on percentile thresholds.

    Usage:
    - Provides momentum-based trading signals.
    - Generates BUY/SELL signals based on 
      RSI thresholds (crossing level 50, reversals from 0/100).
    """

    def calculate_scrsi(
        self, 
        data: PriceDataFrame, 
        config: ScrsiConfigDM
    ) -> pd.DataFrame:
        """
        Computes the SmoothCicle RSI (SCRSI) values.
        Args:
            data (PriceDataFrame): The price dataset containing close prices.
            config (ScrsiConfigDM): Indicator configuration (cycle length, 
            vibration, smoothing).
        Returns:
            pd.DataFrame: A DataFrame containing the SCRSI 
            scaled values and boundary levels.
        """
        # Compute cycle length and cyclic memory for smoothing
        cyclelen = config.domcycle // 2
        cyclicmemory = config.domcycle * 2
        # Calculate RSI components: Up (gains) and Down (losses)
        up = pd.Series(
            np.maximum(
                data.close_prices.diff(), 0
            )
        ).rolling(window=cyclelen).mean()
        down = pd.Series(
            np.minimum(
                data.close_prices.diff(), 0
            )
        ).rolling(window=cyclelen).mean()
        # Standard RSI calculation with safe division 
        # (to avoid division by zero issues)
        rsi = 100 - 100 / (1 + np.divide(
            up, down, 
            out=np.zeros_like(up), 
            where=down != 0)
        )
        # Ensure RSI stays within [0, 100]
        rsi = np.clip(rsi, 0, 100)
        # Convert RSI scale from [0,100] to [-100,100]
        # for better trend visibility
        rsi_scaled = (rsi - 50) * 2
        # Apply cyclic smoothing to RSI
        torque = 2.0 / (config.vibration + 1)
        phasingLag = (config.vibration - 1) // 2
        crsi = np.zeros_like(rsi_scaled)
        # Apply smoothing logic using vectorization
        mask = np.arange(len(rsi_scaled)) >= phasingLag
        crsi[mask] = torque * (
            2 * rsi_scaled[mask] - np.roll(
                rsi_scaled, phasingLag
            )[mask]
        ) + (1 - torque) * np.roll(crsi, 1)[mask]
        # Remove NaN values before calculating boundary levels
        crsi_clean = crsi[~np.isnan(crsi)]
        # Define lower and upper bounds using percentile thresholds
        db = float(
            np.percentile(
                crsi_clean[:cyclicmemory], config.leveling
            ) if len(
                crsi_clean[:cyclicmemory]
            ) > 0 else -100
        )
        ub = float(
            np.percentile(
                crsi_clean[:cyclicmemory], 
                100 - config.leveling
            ) if len(
                crsi_clean[:cyclicmemory]
            ) > 0 else 100
        )
        # Ensure arrays are 1D before storing results
        crsi = crsi.flatten()
        rsi_scaled = rsi_scaled.flatten()
        return pd.DataFrame({
            'CRSI Scaled': rsi_scaled,
            'Lower Bound': db,
            'Upper Bound': ub
        }, index=data.index)

    def generate_scrsi_signals(
        self, 
        data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Generates trading signals based on SCRSI levels.
        Signals:
        - Buy: RSI crossing above level 50 or bouncing from 0 (oversold zone).
        - Sell: RSI crossing below level 50 or bouncing from 100 (overbought zone).
        Args:
            data (pd.DataFrame): DataFrame containing SCRSI values.
        Returns:
            pd.DataFrame: A DataFrame with separate buy and sell signal series.
        """
        # Create a series for BUY signals (0 = no signal, 1 = buy)
        buy_signals = pd.Series(0, index=data.index)
        # Buy signal: Crossing 50 from below
        buy_signals[
            (
                data["CRSI Scaled"].shift(1) < 50
            ) & (
                data["CRSI Scaled"] >= 50
            )
        ] = 1  
        # Buy signal: Reversal from oversold region (0)
        buy_signals[
            (
                data["CRSI Scaled"].shift(1) <= 0
            ) & (
                data["CRSI Scaled"] > 0
            )
        ] = 1
        # Create a series for SELL signals (0 = no signal, 1 = sell)
        sell_signals = pd.Series(0, index=data.index)
        # Sell signal: Crossing 50 from above
        sell_signals[
            (
                data["CRSI Scaled"].shift(1) > 50
            ) & (
                data["CRSI Scaled"] <= 50
            )
        ] = 1
        # Sell signal: Reversal from overbought region (100)
        sell_signals[
            (
                data["CRSI Scaled"].shift(1) >= 100
            ) & (
                data["CRSI Scaled"] < 100
            )
        ] = 1  
        return pd.DataFrame(
            {
                "buy_signals": buy_signals, 
                "sell_signals": sell_signals
            }, 
            index=data.index
        )

    def get_last_signal(
        self, 
        data: PriceDataFrame, 
        config: ScrsiConfigDM
    ) -> str | None:
        """
        Determines the last trading signal based on SCRSI.
        - If the last bar has a buy signal → returns "long".
        - If the last bar has a sell signal → returns "short".
        - If no signal is detected → returns None.
        Args:
            data (PriceDataFrame): Market data.
            config (ScrsiConfigDM): SCRSI indicator configuration.
        Returns:
            str | None: "long" if buy signal, "short" if sell signal, 
            or None if no signal is present.
        """
        # Compute SCRSI values
        scrsi_df = self.calculate_scrsi(data, config)
        # Generate trading signals
        signals_df = self.generate_scrsi_signals(scrsi_df)
        # Check the last signal and return appropriate action
        if signals_df["buy_signals"].iloc[-1] == 1:
            return "long"
        elif signals_df["sell_signals"].iloc[-1] == 1:
            return "short"
        return None
