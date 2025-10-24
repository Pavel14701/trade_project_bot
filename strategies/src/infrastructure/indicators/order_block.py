from typing import Any, Tuple, cast
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy.signal import find_peaks  # type: ignore

from strategies.src.domain.entities import OrderBlockDetectorDM
from strategies.src.infrastructure._types import PriceDataFrame


class OrderBlockDetector:
    """
    Order Block Detector based on ZigZag peak and valley analysis.

    This class identifies potential supply and demand zones (order blocks) in price data
    by detecting local highs and lows using the ZigZag pattern algorithm. It also validates
    these zones through retest, volume confirmation, ATR-based sizing, and liquidity clustering.

    Features:
    - ZigZag detection using `scipy.signal.find_peaks`
    - ATR-based dynamic zone sizing
    - Volume confirmation on breakout and retest
    - Liquidity cluster detection via local extrema proximity
    """

    def zigzag_indicator(
        self, 
        data: PriceDataFrame, 
        config: OrderBlockDetectorDM
    ) -> pd.DataFrame:
        """
        Detects local peaks and valleys in price data using ZigZag pattern logic.

        Applies `find_peaks` to both high and low price series to identify significant turning points.
        These points are filtered using configurable parameters to reduce noise.

        Args:
            data (PriceDataFrame): Price data with high and low price series.
            config (OrderBlockDetectorDM): Configuration for peak detection.

        Returns:
            pd.DataFrame: DataFrame with columns:
                - "peaks": High price values at detected peaks, NaN elsewhere
                - "valleys": Low price values at detected valleys, NaN elsewhere
        """
        peaks = self._detect_peaks(data.high_prices, config, is_peak=True)
        valleys = self._detect_peaks(data.low_prices, config, is_peak=False)

        peaks_array = self._mark_extremes(data.high_prices, peaks)
        valleys_array = self._mark_extremes(data.low_prices, valleys)

        return pd.DataFrame({"peaks": peaks_array, "valleys": valleys_array}, index=data.index)

    def identify_order_blocks(
        self,
        data: PriceDataFrame,
        zigzag_df: pd.DataFrame,
        lookback: int = 20,
        confirmation_window: int = 10,
        min_reaction_size: float = 0.002,
        atr_period: int = 14,
        volume_window: int = 20,
        liquidity_window: int = 10,
        liquidity_tolerance: float = 0.001
    ) -> pd.DataFrame:
        """
        Identifies and confirms order blocks using breakout logic, volume, ATR, and liquidity clustering.

        Args:
            data (PriceDataFrame): Price data with high, low, close, and volume.
            zigzag_df (pd.DataFrame): Output from `zigzag_indicator`.
            lookback (int): Number of candles to look back for peak/valley.
            confirmation_window (int): Number of candles to wait for retest.
            min_reaction_size (float): Minimum % move to confirm reaction.
            atr_period (int): Period for ATR-based zone sizing.
            volume_window (int): Rolling window for average volume.
            liquidity_window (int): Rolling window for local extrema.
            liquidity_tolerance (float): Max distance to consider liquidity cluster.

        Returns:
            pd.DataFrame: Confirmed order blocks with columns:
                - "type": "supply" or "demand"
                - "start": Timestamp of peak/valley
                - "break": Timestamp of breakout
                - "retest": Timestamp of retest
                - "zone_low": Lower bound of block
                - "zone_high": Upper bound of block
        """
        atr = self._calculate_atr(data, atr_period)
        avg_volume = data.volume.rolling(window=volume_window).mean()
        local_highs = data.high_prices.rolling(window=liquidity_window).max()
        local_lows = data.low_prices.rolling(window=liquidity_window).min()

        blocks = []
        for i in range(lookback, len(data) - confirmation_window):
            idx = i - lookback
            close = data.close_prices.iloc[idx]
            atr_value = atr.iloc[idx]
            zone_low = close - atr_value
            zone_high = close + atr_value

            if not np.isnan(zigzag_df.peaks.iloc[idx]):
                if self._is_valid_breakout(data, idx, i, avg_volume, direction="down"):
                    if self._has_liquidity_cluster(data.low_prices, idx, local_lows, liquidity_tolerance):
                        block = self._confirm_supply_block(data, idx, i, confirmation_window, zone_low, zone_high, avg_volume, min_reaction_size)
                        if block:
                            blocks.append(block)

            elif not np.isnan(zigzag_df.valleys.iloc[idx]):
                if self._is_valid_breakout(data, idx, i, avg_volume, direction="up"):
                    if self._has_liquidity_cluster(data.high_prices, idx, local_highs, liquidity_tolerance):
                        block = self._confirm_demand_block(data, idx, i, confirmation_window, zone_low, zone_high, avg_volume, min_reaction_size)
                        if block:
                            blocks.append(block)

        return pd.DataFrame(blocks)

    # --- Internal methods ---

    def _detect_peaks(self, series: pd.Series, config: OrderBlockDetectorDM, is_peak: bool) -> NDArray[np.intp]:
        """
        Applies `find_peaks` to a price series.

        Args:
            series (pd.Series): Price series (high or low).
            config (OrderBlockDetectorDM): Peak detection config.
            is_peak (bool): True for peaks, False for valleys.

        Returns:
            NDArray[np.intp]: Indices of detected peaks/valleys.
        """
        prominence = config.peak_prominance if is_peak else config.valley_prominance
        result = find_peaks(
            x=series,
            height=config.height,
            threshold=config.threshold,
            distance=config.distance,
            prominence=prominence,
            width=config.width,
            wlen=config.wlen,
            rel_height=config.rel_height,
            plateau_size=config.plateu_size
        )
        return cast(Tuple[NDArray[np.intp], dict[str, Any]], result)[0]

    def _mark_extremes(self, series: pd.Series, indices: NDArray[np.intp]) -> NDArray[np.float64]:
        """
        Marks detected peaks/valleys in a NaN-filled array.

        Args:
            series (pd.Series): Original price series.
            indices (NDArray): Indices of detected points.

        Returns:
            NDArray[np.float64]: Array with values at indices, NaN elsewhere.
        """
        arr = np.full_like(series.to_numpy(), np.nan, dtype=np.float64)
        arr[indices] = series.iloc[indices]
        return arr

    def _calculate_atr(self, data: PriceDataFrame, period: int) -> pd.Series:
        """
        Calculates ATR as high - low over a rolling window.

        Args:
            data (PriceDataFrame): Price data.
            period (int): ATR period.

        Returns:
            pd.Series: ATR values.
        """
        return data.high_prices.rolling(window=period).max() - data.low_prices.rolling(window=period).min()

    def _is_valid_breakout(self, data: PriceDataFrame, idx: int, i: int, avg_volume: pd.Series, direction: str) -> bool:
        """
        Checks if breakout is valid based on price and volume.

        Args:
            data (PriceDataFrame): Price data.
            idx (int): Index of peak/valley.
            i (int): Index of breakout.
            avg_volume (pd.Series): Rolling average volume.
            direction (str): "up" or "down".

        Returns:
            bool: True if breakout is valid.
        """
        if direction == "down":
            return data.low_prices.iloc[i] < data.low_prices.iloc[idx] and data.volume.iloc[i] > avg_volume.iloc[i]
        else:
            return data.high_prices.iloc[i] > data.high_prices.iloc[idx] and data.volume.iloc[i] > avg_volume.iloc[i]

    def _has_liquidity_cluster(self, series: pd.Series, idx: int, local_extremes: pd.Series, tolerance: float) -> bool:
        """
        Checks if price is near local extrema (liquidity cluster).

        Args:
            series (pd.Series): Price series.
            idx (int): Index to check.
            local_extremes (pd.Series): Rolling max/min series.
            tolerance (float): Max distance to consider cluster.

        Returns:
            bool: True if cluster is present.
        """
        return abs(local_extremes.iloc[idx] - series.iloc[idx]) < tolerance

    def _confirm_supply_block(
        self,
        data: PriceDataFrame,
        idx: int,
        breakout_idx: int,
        window: int,
        zone_low: float,
        zone_high: float,
        avg_volume: pd.Series,
        min_reaction_size: float
    ) -> dict | None:
        """
        Confirms a supply block by checking for a valid retest and bearish reaction.

        Conditions:
        - Retest candle must fall within the zone
        - Volume must exceed average
        - Close must be below zone_low
        - Reaction size must exceed threshold

        Args:
            data (PriceDataFrame): Price data.
            idx (int): Index of peak.
            breakout_idx (int): Index of breakout.
            window (int): Number of candles to wait for retest.
            zone_low (float): Lower bound of block.
            zone_high (float): Upper bound of block.
            avg_volume (pd.Series): Rolling average volume.
            min_reaction_size (float): Minimum % move to confirm reaction.

        Returns:
            dict | None: Confirmed block info or None.
        """
        for j in range(breakout_idx + 1, breakout_idx + window):
            if zone_low <= data.low_prices.iloc[j] <= zone_high and data.volume.iloc[j] > avg_volume.iloc[j]:
                if data.close_prices.iloc[j] < zone_low and \
                   (zone_low - data.close_prices.iloc[j]) / zone_low >= min_reaction_size:
                    return {
                        "type": "supply",
                        "start": data.index[idx],
                        "break": data.index[breakout_idx],
                        "retest": data.index[j],
                        "zone_low": zone_low,
                        "zone_high": zone_high
                    }
        return None

    def _confirm_demand_block(
        self,
        data: PriceDataFrame,
        idx: int,
        breakout_idx: int,
        window: int,
        zone_low: float,
        zone_high: float,
        avg_volume: pd.Series,
        min_reaction_size: float
    ) -> dict | None:
        """
        Confirms a demand block by checking for a valid retest and bullish reaction.

        Conditions:
        - Retest candle must fall within the zone
        - Volume must exceed average
        - Close must be above zone_high
        - Reaction size must exceed threshold

        Args:
            data (PriceDataFrame): Price data.
            idx (int): Index of valley.
            breakout_idx (int): Index of breakout.
            window (int): Number of candles to wait for retest.
            zone_low (float): Lower bound of block.
            zone_high (float): Upper bound of block.
            avg_volume (pd.Series): Rolling average volume.
            min_reaction_size (float): Minimum % move to confirm reaction.

        Returns:
            dict | None: Confirmed block info or None.
        """
        for j in range(breakout_idx + 1, breakout_idx + window):
            if zone_low <= data.high_prices.iloc[j] <= zone_high and data.volume.iloc[j] > avg_volume.iloc[j]:
                if data.close_prices.iloc[j] > zone_high and \
                   (data.close_prices.iloc[j] - zone_high) / zone_high >= min_reaction_size:
                    return {
                        "type": "demand",
                        "start": data.index[idx],
                        "break": data.index[breakout_idx],
                        "retest": data.index[j],
                        "zone_low": zone_low,
                        "zone_high": zone_high
                    }
        return None
