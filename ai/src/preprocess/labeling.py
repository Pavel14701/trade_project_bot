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
        if evt is None:
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
    hits: list[tuple[str, int]] = []
    if np.any(highs >= long_tp): hits.append(("BUY_TP", int(np.argmax(highs >= long_tp))))
    if np.any(lows <= long_sl): hits.append(("BUY_SL", int(np.argmax(lows <= long_sl))))
    if np.any(lows <= short_tp): hits.append(("SELL_TP", int(np.argmax(lows <= short_tp))))
    if np.any(highs >= short_sl): hits.append(("SELL_SL", int(np.argmax(highs >= short_sl))))
    return min(hits, key=lambda x: x[1]) if hits else (None, None)
