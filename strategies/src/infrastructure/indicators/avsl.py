import pandas as pd
import numpy as np
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
        Custom price function for AVSL calculation.
        Args:
            data (PriceDataFrame): Market price dataset.
            vpc (pd.Series): Volume Price Confirmation values.
            vpr (pd.Series): Volume Price Ratio values.
            vpci (pd.Series): VPCI values.
        Returns:
            NDArray: Adjusted price levels based on volume-price interaction.
        """
        PriceV = np.zeros_like(vpc)
        for i in range(len(vpc)):
            if np.isnan(vpci.iloc[i]):
                lenV = 0
            else:
                lenV = int(
                    round(abs(vpci.iloc[i] - 3))
                ) if vpc.iloc[i] < 0 else round(
                    vpci.iloc[i] + 3
                )
            VPCc = -1 if (
                vpc.iloc[i] > -1
            ) & (
                vpc.iloc[i] < 0
            ) else 1 if (
                vpc.iloc[i] < 1
            ) & (
                vpc.iloc[i] >= 0
            ) else vpc.iloc[i]
            Price = np.sum(
                data.low_prices.iloc[
                    i - lenV + 1:i + 1
                ] / VPCc / vpr.iloc[
                    i - lenV + 1:i + 1
                ]
            ) if lenV > 0 else data.low_prices.iloc[i]
            PriceV[i] = Price / lenV / 100 if lenV > 0 else Price
        return PriceV

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
