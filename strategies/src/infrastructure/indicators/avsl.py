import pandas as pd
import numpy as np
from numba import njit
from numpy.typing import NDArray
import pandas_ta as ta

from strategies.src.domain.entities import AvslConfigDM
from strategies.src.infrastructure._types import PriceDataFrame


class AVSL:
    """
    Adaptive Volume-Weighted Support Level 
      (AVSL) Indicator Implementation.

    The AVSL indicator calculates **dynamic 
      support and resistance levels** using volume-weighted 
      moving averages and volatility metrics.

    Formula:
    1. Compute VWMA (**Volume-Weighted Moving Average**) 
      over fast and slow periods.
    2. Calculate **Volume Price Confirmation (VPC)** to 
      measure price deviations.
    3. Compute **Volume Price Ratio (VPR)** by dividing 
      fast VWMA by a simple moving average.
    4. Determine **Volume Momentum (VM)** by comparing 
      fast and slow volume trends.
    5. Combine VPC, VPR, and VM into **VPCI** for 
      trend confirmation.
    6. Apply a **custom price function** to 
      adjust support/resistance levels.
    7. Use a smoothed moving average (**SMA**) 
      to finalize AVSL levels.

    Usage:
    - Identifies **strong support zones** based 
      on price and volume dynamics.
    - Provides adaptive thresholds for **trend 
      validation and risk management**.
    """

    def calculate_avsl(
        self, 
        data: PriceDataFrame, 
        config: AvslConfigDM
    ) -> pd.DataFrame:
        """
        Computes the AVSL (Adaptive Support Level) values.
        Args:
            data (PriceDataFrame): Market price dataset containing 
              high, low, close prices and volume.
            config (AvslConfigDM): AVSL configuration parameters.
        Returns:
            pd.DataFrame: A DataFrame containing AVSL 
              values indexed by date.
        """
        # Compute VWMA (Volume-Weighted Moving Average)
        #  for fast and slow periods
        vw_ma_fast: pd.Series = ta.vwma(
            close=data.close_prices, 
            volume=data.volumes, 
            length=config.length_fast
        )
        vw_ma_slow: pd.Series = ta.vwma(
            close=data.close_prices, 
            volume=data.volumes,
            length=config.length_slow
        )
        # Compute Volume Price Confirmation (VPC)
        vpc: pd.Series = vw_ma_slow - ta.sma(
            close=data.close_prices, 
            length=config.length_slow,
            talib=True
        )
        # Compute Volume Price Ratio (VPR)
        vpr: pd.Series = vw_ma_fast / ta.sma(
            close=data.close_prices, 
            length=config.length_fast, 
            talib=True
        )
        # Compute Volume Momentum (VM)
        vm: pd.Series = ta.sma(
            close=data.volumes, 
            length=config.length_fast, 
            talib=True
        ) / ta.sma(
            close=data.volumes, 
            length=config.length_slow,
            talib=True
        )
        # Compute Volume Price Confirmation Index (VPCI)
        vpci: pd.Series = vpc * vpr * vm
        # Compute custom price adjustment function
        PriceV = self._price_fun(data, vpc, vpr, vpci)
        # Compute AVSL deviation factor
        deviation = config.stand_div * vpci * vm
        # Compute final AVSL level using SMA
        avsl = ta.sma(
            close=data.low_prices - PriceV + deviation,
            length=config.length_slow, 
            talib=True
        )
        return pd.DataFrame({"avsl": avsl}, index=data.index)


    def _price_fun(
        self,
        data: PriceDataFrame,
        vpc: pd.Series,
        vpr: pd.Series,
        vpci: pd.Series,
    ) -> NDArray:
        """
        Optimized price adjustment function using 
          vectorized calculations and a 
          Numba-jitted helper.

        Args:
            data (PriceDataFrame): Market price dataset.
            vpc (pd.Series): Volume Price Confirmation values.
            vpr (pd.Series): Volume Price Ratio values.
            vpci (pd.Series): VPCI values.

        Returns:
            np.ndarray: Adjusted price levels based 
              on volume-price interaction.
        """
        # Convert pandas Series to NumPy arrays for faster processing
        low_np = data.low_prices.to_numpy()
        vpc_np = vpc.to_numpy()
        vpr_np = vpr.to_numpy()
        vpci_np = vpci.to_numpy()
        # Vectorized calculation of lenV
        lenV = np.where(
            np.isnan(vpci_np), 1,  # Prevent division by zero
            np.where(
                vpc_np < 0,
                np.round(np.abs(vpci_np - 3)).astype(np.int32),
                np.round(vpci_np + 3).astype(np.int32),
            )
        )
        # Vectorized calculation of VPCc
        VPCc = np.where(
            (vpc_np > -1) & (vpc_np < 0),
            -1.0,
            np.where(
                (
                    vpc_np >= 0
                ) & (
                    vpc_np < 1
                ), 1.0, vpc_np
            ),
        )
        # Call the optimized JIT helper function
        return _compute_price_v(
            low_np, vpr_np, lenV, VPCc
        )

    def get_last_avsl_signal(
            self, 
            data: PriceDataFrame, 
            config: AvslConfigDM
        ) -> float | None:
        """
        Retrieves the AVSL value on the last bar.
        Args:
            data (PriceDataFrame): Market data with price information.
            config (AvslConfigDM): Configuration settings for AVSL.
        Returns:
            float | None: AVSL value of the last bar if available, otherwise None.
        """
        # Compute AVSL values
        avsl_df = self.calculate_avsl(data, config)
        # Ensure AVSL is not empty before retrieving the last value
        if avsl_df.empty or pd.isna(avsl_df["avsl"].iloc[-1]):
            return None
        return avsl_df["avsl"].iloc[-1]


from numba import njit
import numpy as np

@njit
def _compute_price_v(
    low: NDArray, 
    vpr: NDArray, 
    lenV: NDArray, 
    VPCc: NDArray
) -> NDArray:
    """
    Optimized price computation using Numba JIT for speed.

    Args:
        low (np.ndarray): Array of low prices.
        vpr (np.ndarray): Volume Price Ratio.
        lenV (np.ndarray): Length value for price calculation.
        VPCc (np.ndarray): Adjusted VPC coefficient.
    Returns:
        np.ndarray: Optimized price values.
    """
    n = low.shape[0]
    out = np.empty(n, dtype=np.float64)
    for i in range(n):
        L = lenV[i]
        if L > 0:
            s = np.sum(
                np.divide(
                    low[max(0, i - L + 1): i + 1], 
                    VPCc[i] * vpr[max(0, i - L + 1): i + 1], 
                    out=np.zeros_like(
                        low[max(0, i - L + 1): i + 1]
                    ),
                    # Prevent division by zero
                    where=(
                        VPCc[i] != 0
                    ) & (
                        vpr[max(0, i - L + 1): i + 1] != 0
                    )
                )
            )
            out[i] = s / L / 100.0
        else:
            out[i] = low[i]
    return out