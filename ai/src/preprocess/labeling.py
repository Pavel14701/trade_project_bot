# ai/src/preprocess/labeling.py

import pandas as pd
import numpy as np
from numpy.typing import NDArray

def label_first_touch(
    df: pd.DataFrame,
    asset_col: str,
    close_col: str = "close",
    high_col: str = "high",
    low_col: str = "low",
    sl_col: str = "sl_pct",
    tp_col: str = "tp_pct",
    lag_bars: int = 1,
    horizon_bars: int = 64
) -> pd.DataFrame:
    """
    Assigns directional labels based on first-touch logic.

    For each asset, evaluates whether price hits take-profit or stop-loss thresholds
    within a future horizon after a lag. Labels are assigned based on which event
    occurs first: BUY_TP, BUY_SL, SELL_TP, or SELL_SL.

    Parameters:
        df (pd.DataFrame): Input dataframe with OHLC and threshold columns.
        asset_col (str): Column identifying asset groups.
        close_col (str): Column with close prices.
        high_col (str): Column with high prices.
        low_col (str): Column with low prices.
        sl_col (str): Column with stop-loss percentage.
        tp_col (str): Column with take-profit percentage.
        lag_bars (int): Number of bars to lag before evaluation.
        horizon_bars (int): Number of bars ahead to monitor for first-touch.

    Returns:
        pd.DataFrame: Copy of input with added columns:
            - "signal": 1 for BUY, 2 for SELL
            - "success": 1 if TP hit first, 0 if SL hit first
            - "t_first": Offset (in bars) to first hit event
    """
    out = df.copy()
    signal = np.zeros(len(out), dtype=np.int8)
    success = np.zeros(len(out), dtype=np.int8)
    t_first = np.full(len(out), np.nan)
    for _, g in out.groupby(asset_col):  # type: ignore
        _process_group(
            g, signal, success, t_first,
            close_col, high_col, low_col, sl_col, tp_col,
            lag_bars, horizon_bars
        )
    out["signal"] = signal
    out["success"] = success
    out["t_first"] = t_first
    return out

def _process_group(
    g: pd.DataFrame,
    signal: NDArray[np.int8],
    success: NDArray[np.int8],
    t_first: NDArray[np.float64],
    close_col: str,
    high_col: str,
    low_col: str,
    sl_col: str,
    tp_col: str,
    lag_bars: int,
    horizon_bars: int
) -> None:
    """
    Processes a single asset group and updates label arrays.

    Iterates over each row, computes entry price, thresholds, and checks
    future price segments for first-touch events.

    Parameters:
        g (pd.DataFrame): Subset of rows for a single asset.
        signal (NDArray): Array to store directional labels.
        success (NDArray): Array to store TP/SL success flags.
        t_first (NDArray): Array to store time-to-event offsets.
        close_col, high_col, low_col, sl_col, tp_col: Column names.
        lag_bars (int): Bars to skip before evaluation.
        horizon_bars (int): Bars ahead to monitor.
    """
    idxs = g.index.to_numpy(dtype=np.int64)
    closes = g[close_col].to_numpy(dtype=np.float64)
    highs = g[high_col].to_numpy(dtype=np.float64)
    lows = g[low_col].to_numpy(dtype=np.float64)
    sl_p = g[sl_col].to_numpy(dtype=np.float64)
    tp_p = g[tp_col].to_numpy(dtype=np.float64)
    for i in range(len(g)):
        start = i + lag_bars
        if start >= len(g):
            break
        entry = closes[i]
        sl, tp = sl_p[i], tp_p[i]
        long_tp, long_sl = entry * (1 + tp), entry * (1 - sl)
        short_tp, short_sl = entry * (1 - tp), entry * (1 + sl)
        j_end = min(len(g), start + horizon_bars)
        h_seg, l_seg = highs[start:j_end], lows[start:j_end]
        evt, t = _first_hit(long_tp, long_sl, short_tp, short_sl, h_seg, l_seg)
        if evt is None or t is None:
            continue
        global_i = idxs[i]
        signal[global_i] = 1 if evt.startswith("BUY") else 2
        success[global_i] = 1 if evt.endswith("TP") else 0
        t_first[global_i] = t + 1

def _first_hit(
    long_tp: float,
    long_sl: float,
    short_tp: float,
    short_sl: float,
    highs: NDArray[np.float64],
    lows: NDArray[np.float64]
) -> tuple[str, int] | tuple[None, None]:
    """
    Determines which threshold was hit first in a future segment.

    Evaluates whether price hits long/short TP or SL levels, and returns
    the earliest event.

    Parameters:
        long_tp (float): Long take-profit threshold.
        long_sl (float): Long stop-loss threshold.
        short_tp (float): Short take-profit threshold.
        short_sl (float): Short stop-loss threshold.
        highs (NDArray): High prices in future segment.
        lows (NDArray): Low prices in future segment.

    Returns:
        tuple[str, int]: Event label and offset index.
        tuple[None, None]: If no threshold was hit.
    """
    hits: list[tuple[str, int]] = []
    if np.any(highs >= long_tp): hits.append(("BUY_TP", int(np.argmax(highs >= long_tp))))
    if np.any(lows <= long_sl): hits.append(("BUY_SL", int(np.argmax(lows <= long_sl))))
    if np.any(lows <= short_tp): hits.append(("SELL_TP", int(np.argmax(lows <= short_tp))))
    if np.any(highs >= short_sl): hits.append(("SELL_SL", int(np.argmax(highs >= short_sl))))
    return min(hits, key=lambda x: x[1]) if hits else (None, None)
