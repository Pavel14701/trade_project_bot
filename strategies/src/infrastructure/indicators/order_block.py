from typing import Any, Tuple, cast
import numpy as np
import pandas as pd
import pandas_ta as ta
from numpy.typing import NDArray
from scipy.signal import find_peaks  # type: ignore

from strategies.src.domain.entities import OrderBlockDetectorDM
from strategies.src.infrastructure._types import PriceDataFrame


class OrderBlockDetector:
    """
    Order Block Detector based on ZigZag peak and valley analysis.

    This class identifies potential supply and demand zones (order blocks) in price data
    by detecting local highs and lows using the ZigZag pattern algorithm. It validates
    these zones through breakout logic, volume confirmation, ATR-based sizing, and liquidity clustering.
    """

    def zigzag_indicator(
        self, 
        data: PriceDataFrame, 
        config: OrderBlockDetectorDM
    ) -> pd.DataFrame:
        """
        Detects local peaks and valleys in price data using ZigZag pattern logic.
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
        Full pipeline for detecting and confirming order blocks.
        """
        indicators = self._precompute_indicators(data, atr_period, volume_window, liquidity_window)
        candidates = self._generate_block_candidates(data, zigzag_df, indicators, lookback, liquidity_tolerance)
        confirmed = self._validate_block_candidates(data, candidates, indicators, confirmation_window, min_reaction_size)
        return pd.DataFrame(confirmed)

    # --- Stage 1: Precomputation ---

    def _precompute_indicators(
        self,
        data: PriceDataFrame,
        atr_period: int,
        volume_window: int,
        liquidity_window: int
    ) -> dict:
        atr = self._calculate_atr(data, atr_period)
        avg_volume = data.volume.rolling(window=volume_window).mean()
        local_highs = data.high_prices.rolling(window=liquidity_window).max()
        local_lows = data.low_prices.rolling(window=liquidity_window).min()
        zone_low = data.close_prices - atr
        zone_high = data.close_prices + atr
        return {
            "atr": atr,
            "avg_volume": avg_volume,
            "local_highs": local_highs,
            "local_lows": local_lows,
            "zone_low": zone_low,
            "zone_high": zone_high
        }

    # --- Stage 2: Candidate generation ---

    def _generate_block_candidates(
        self,
        data: PriceDataFrame,
        zigzag_df: pd.DataFrame,
        indicators: dict,
        lookback: int,
        liquidity_tolerance: float
    ) -> list[dict]:
        candidates = []
        for i in range(lookback, len(data)):
            idx = i - lookback
            if not np.isnan(zigzag_df.peaks.iloc[idx]):
                if self._has_liquidity_cluster(data.low_prices, idx, indicators["local_lows"], liquidity_tolerance):
                    candidates.append({"type": "supply", "idx": idx, "break_idx": i})
            elif not np.isnan(zigzag_df.valleys.iloc[idx]):
                if self._has_liquidity_cluster(data.high_prices, idx, indicators["local_highs"], liquidity_tolerance):
                    candidates.append({"type": "demand", "idx": idx, "break_idx": i})
        return candidates

    # --- Stage 3: Candidate validation ---

    def _validate_block_candidates(
        self,
        data: PriceDataFrame,
        candidates: list[dict],
        indicators: dict,
        confirmation_window: int,
        min_reaction_size: float,
    ) -> list[dict]:
        confirmed = []
        avg_volume = indicators["avg_volume"]
        zone_low_series = indicators["zone_low"]
        zone_high_series = indicators["zone_high"]

        for c in candidates:
            idx = c["idx"]
            breakout_idx = c["break_idx"]
            is_supply = c["type"] == "supply"
            direction = "down" if is_supply else "up"

            if not self._is_valid_breakout(data, idx, breakout_idx, avg_volume, direction):
                continue

            block = self._confirm_block(
                data=data,
                idx=idx,
                breakout_idx=breakout_idx,
                window=confirmation_window,
                zone_low=zone_low_series.iloc[idx],
                zone_high=zone_high_series.iloc[idx],
                avg_volume=avg_volume,
                min_reaction_size=min_reaction_size,
                is_supply=is_supply,
            )
            if block:
                confirmed.append(block)

        return confirmed

    # --- Core utilities ---

    def _detect_peaks(self, series: pd.Series, config: OrderBlockDetectorDM, is_peak: bool) -> NDArray[np.intp]:
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
        arr = np.full_like(series.to_numpy(), np.nan, dtype=np.float64)
        arr[indices] = series.iloc[indices]
        return arr

    def _calculate_atr(self, data: PriceDataFrame, period: int) -> pd.Series:
        """
        Calculates ATR using pandas_ta with TA-Lib backend.
        """
        return ta.atr(
            high=data.high_prices,
            low=data.low_prices,
            close=data.close_prices,
            length=period,
            talib=True
        )

    def _is_valid_breakout(self, data: PriceDataFrame, idx: int, i: int, avg_volume: pd.Series, direction: str) -> bool:
        if direction == "down":
            return data.low_prices.iloc[i] < data.low_prices.iloc[idx] and data.volume.iloc[i] > avg_volume.iloc[i]
        else:
            return data.high_prices.iloc[i] > data.high_prices.iloc[idx] and data.volume.iloc[i] > avg_volume.iloc[i]

    def _has_liquidity_cluster(self, series: pd.Series, idx: int, local_extremes: pd.Series, tolerance: float) -> bool:
        return abs(local_extremes.iloc[idx] - series.iloc[idx]) < tolerance

    def _confirm_block(
        self,
        data: PriceDataFrame,
        idx: int,
        breakout_idx: int,
        window: int,
        zone_low: float,
        zone_high: float,
        avg_volume: pd.Series,
        min_reaction_size: float,
        is_supply: bool,
    ) -> dict | None:
        test_series = data.low_prices if is_supply else data.high_prices
        close = data.close_prices
        volume = data.volume
        block_type = "supply" if is_supply else "demand"

        for j in range(breakout_idx + 1, breakout_idx + window):
            price_j = test_series.iloc[j]
            close_j = close.iloc[j]
            volume_j = volume.iloc[j]

            if not (zone_low <= price_j <= zone_high and volume_j > avg_volume.iloc[j]):
                continue

            reaction = ((zone_low - close_j) / zone_low) if is_supply else ((close_j - zone_high) / zone_high)
            if reaction >= min_reaction_size:
                return {
                    "type": block_type,
                    "start": data.index[idx],
                    "break": data.index[breakout_idx],
                    "retest": data.index[j],
                    "zone_low": zone_low,
                    "zone_high": zone_high,
                }

        return None
