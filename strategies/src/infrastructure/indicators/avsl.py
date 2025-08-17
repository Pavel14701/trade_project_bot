from typing import cast

import pandas as pd
import numpy as np
from numba import njit  # type: ignore
from numpy.typing import NDArray
import pandas_ta as ta  # type: ignore

from strategies.src.domain.entities import AvslConfigDM
from strategies.src.infrastructure._types import PriceDataFrame


class AVSL:
    """
    Adaptive Volume-Weighted Support Level (AVSL) Indicator.

    This indicator calculates dynamic support levels based on volume, price movement,
    and volatility. It is designed to adapt to changing market conditions by incorporating
    volume-weighted price behavior and momentum.

    Core Components:
    - VWMA (Volume-Weighted Moving Average): Reflects price levels weighted by trading volume.
    - VPC (Volume Price Confirmation): Measures the difference between volume-weighted and simple moving averages.
    - VPR (Volume-Price Ratio): Captures the relationship between volume and price.
    - VM (Volume Momentum): Indicates the strength of volume trends.
    - VPCI (Volume Price Confirmation Index): A composite metric combining VPC, VPR, and VM.
    - AVSL (Adaptive Support Level): A smoothed support level derived from price and volume dynamics.
    """

    def calculate_avsl(
        self,
        data: PriceDataFrame,
        config: AvslConfigDM
    ) -> pd.DataFrame:
        """
        Calculates the AVSL indicator values for the given market data.

        This method computes the core AVSL components and derives a smoothed support level
        using volume-adjusted price deviations.

        Args:
            data (PriceDataFrame): Historical market data containing close, low prices and volume.
            config (AvslConfigDM): Configuration parameters including moving average lengths and deviation factor.

        Returns:
            pd.DataFrame: A DataFrame containing the AVSL values indexed by time.
        """
        vw_f, vw_s, vpc, vpr, vm, vpci = self._compute_base_series(data, config)  # type: ignore
        price_v = self._price_fun(data, vpc, vpr, vpci)
        deviation: pd.Series[float] = config.stand_div * vpci * vm  # type: ignore
        avsl = ta.sma(  # type: ignore
            close=data.low_prices - price_v + deviation,
            length=config.length_slow,
            talib=True
        )
        if avsl is None:
            raise ValueError("AVSL SMA calculation failed")
        return pd.DataFrame({"avsl": avsl}, index=data.index)  # type: ignore

    def _compute_base_series(
        self,
        data: PriceDataFrame,
        config: AvslConfigDM
    ) -> tuple[
        pd.Series[float],
        pd.Series[float],
        pd.Series[float],
        pd.Series[float],
        pd.Series[float],
        pd.Series[float]
    ]:
        """
        Computes the foundational time series required for AVSL calculation.

        This includes volume-weighted and simple moving averages for price and volume,
        as well as derived metrics that reflect volume-price dynamics.

        Args:
            data (PriceDataFrame): Historical market data including close prices and volumes.
            config (AvslConfigDM): Configuration parameters specifying fast and slow lengths.

        Returns:
            tuple: A tuple containing six pandas Series:
                - Fast VWMA
                - Slow VWMA
                - VPC (Volume Price Confirmation)
                - VPR (Volume-Price Ratio)
                - VM (Volume Momentum)
                - VPCI (Volume Price Confirmation Index)
        """
        vw_ma_fast_raw = ta.vwma(data.close_prices, data.volumes, config.length_fast)  # type: ignore
        vw_ma_slow_raw = ta.vwma(data.close_prices, data.volumes, config.length_slow)  # type: ignore
        if vw_ma_fast_raw is None or vw_ma_slow_raw is None:
            raise ValueError("VWMA calculation failed")
        sma_fast_raw = ta.sma(data.close_prices, config.length_fast, talib=True)  # type: ignore
        sma_slow_raw = ta.sma(data.close_prices, config.length_slow, talib=True)  # type: ignore
        vol_fast_raw = ta.sma(data.volumes, config.length_fast, talib=True)  # type: ignore
        vol_slow_raw = ta.sma(data.volumes, config.length_slow, talib=True)  # type: ignore
        if sma_fast_raw is None:
            raise ValueError("sma_fast is None")
        if sma_slow_raw is None:
            raise ValueError("sma_slow is None")
        if vol_fast_raw is None:
            raise ValueError("vol_fast is None")
        if vol_slow_raw is None:
            raise ValueError("vol_slow is None")
        vw_ma_fast = cast(pd.Series[float], vw_ma_fast_raw)
        vw_ma_slow = cast(pd.Series[float], vw_ma_slow_raw)
        sma_fast = cast(pd.Series[float], sma_fast_raw)
        sma_slow = cast(pd.Series[float], sma_slow_raw)
        vol_fast = cast(pd.Series[float], vol_fast_raw)
        vol_slow = cast(pd.Series[float], vol_slow_raw)
        vpc: pd.Series[float] = vw_ma_slow - sma_slow  # type: ignore
        vpr: pd.Series[float] = vw_ma_fast / sma_fast  # type: ignore
        vm: pd.Series[float] = vol_fast / vol_slow  # type: ignore
        vpci: pd.Series[float] = vpc * vpr * vm  # type: ignore
        return vw_ma_fast, vw_ma_slow, vpc, vpr, vm, vpci

    def _price_fun(
        self,
        data: PriceDataFrame,
        vpc: pd.Series[float],
        vpr: pd.Series[float],
        vpci: pd.Series[float]
    ) -> NDArray[np.float64]:
        """
        Computes the adjusted price series based on volume-price interaction.

        This function transforms the low price series using dynamic window lengths
        and volume-price coefficients to reflect market pressure and support zones.

        Args:
            data (PriceDataFrame): Historical market data.
            vpc (pd.Series): Volume Price Confirmation series.
            vpr (pd.Series): Volume-Price Ratio series.
            vpci (pd.Series): Volume Price Confirmation Index series.

        Returns:
            np.ndarray: Array of adjusted price values.
        """
        low_np: NDArray[np.float64] = data.low_prices.to_numpy()  # type: ignore
        vpc_np: NDArray[np.float64] = vpc.to_numpy()  # type: ignore
        vpr_np: NDArray[np.float64] = vpr.to_numpy()  # type: ignore
        vpci_np: NDArray[np.float64] = vpci.to_numpy()  # type: ignore
        lenV = self.compute_len_v(vpc_np, vpci_np)
        VPCc = self.compute_vpcc(vpc_np)
        return _compute_price_v(low_np, vpr_np, lenV, VPCc)

    @staticmethod
    def compute_len_v(
        vpc: NDArray[np.float64],
        vpci: NDArray[np.float64]
    ) -> NDArray[np.int32]:
        """
        Computes the dynamic window length for price adjustment based on VPCI values.

        The window length determines how many past values are considered when calculating
        adjusted prices. It adapts based on the strength and direction of volume-price signals.

        Args:
            vpc (np.ndarray): Volume Price Confirmation values.
            vpci (np.ndarray): Volume Price Confirmation Index values.

        Returns:
            np.ndarray: Array of integer window lengths for each time step.
        """
        return np.where(
            np.isnan(vpci), 1,
            np.where(
                vpc < 0,
                np.round(np.abs(vpci - 3)).astype(np.int32),
                np.round(vpci + 3).astype(np.int32)
            )
        )

    @staticmethod
    def compute_vpcc(vpc: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        Applies stability corrections to the VPC coefficient.

        This function ensures that VPC values remain within a stable range to avoid
        division errors or extreme values during price adjustment.

        Args:
            vpc (np.ndarray): Volume Price Confirmation values.

        Returns:
            np.ndarray: Array of corrected VPC coefficients for robust calculations.
        """
        return np.where(
            (vpc > -1) & (vpc < 0), -1.0,
            np.where((vpc >= 0) & (vpc < 1), 1.0, vpc)
        )

    def get_last_avsl_signal(
        self,
        data: PriceDataFrame,
        config: AvslConfigDM
    ) -> float | None:
        """
        Retrieves the most recent AVSL value from the computed series.

        This method is useful for signal generation or decision-making based on
        the latest support level derived from volume and price dynamics.

        Args:
            data (PriceDataFrame): Historical market data.
            config (AvslConfigDM): Configuration parameters for AVSL calculation.

        Returns:
            float | None: The latest AVSL value, or None if the data is empty or invalid.
        """
        avsl_df = self.calculate_avsl(data, config)
        if avsl_df.empty:
            return None
        last_value: float = avsl_df.get("avsl", pd.Series(dtype=float)).iloc[-1]  # type: ignore
        return None if pd.isna(last_value) else float(last_value)  # type: ignore


@njit
def _compute_price_v(
    low: NDArray[np.float64],
    vpr: NDArray[np.float64],
    lenV: NDArray[np.int32],
    VPCc: NDArray[np.float64]
) -> NDArray[np.float64]:
    """
    Performs fast computation of adjusted price values using Numba JIT compilation.

    This function applies a rolling calculation over a dynamic window length (lenV),
    dividing low prices by volume-price coefficients (VPCc * VPR) and averaging the result.
    It is optimized for performance and avoids division by zero using masking.

    Args:
        low (np.ndarray): Array of low price values.
        vpr (np.ndarray): Volume-Price Ratio values.
        lenV (np.ndarray): Dynamic window lengths for each time step.
        VPCc (np.ndarray): Corrected Volume Price Confirmation coefficients.

    Returns:
        np.ndarray: Array of adjusted price values, representing dynamic support levels.
    """
    n = low.shape[0]
    out = np.empty(n, dtype=np.float64)
    for i in range(n):
        L = lenV[i]
        if L > 0:
            start = max(0, i - L + 1)
            denom = VPCc[i] * vpr[start:i + 1]
            valid = (VPCc[i] != 0) & (vpr[start:i + 1] != 0)
            values = np.divide(
                low[start:i + 1],
                denom,
                out=np.zeros_like(low[start:i + 1]),
                where=valid
            )
            out[i] = np.sum(values) / L / 100.0
        else:
            out[i] = low[i]
    return out