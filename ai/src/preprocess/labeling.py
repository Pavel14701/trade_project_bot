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
    for _, g in out.groupby(asset_col): # type: ignore[reportUnknownMemberType]
        g: pd.DataFrame 
        idxs: NDArray[np.int64] = g.index.to_numpy(dtype=np.int64)  # type: ignore[assignment]
        closes: NDArray[np.float64] = g[close_col].to_numpy(dtype=np.float64)  # type: ignore[assignment]
        highs: NDArray[np.float64] = g[high_col].to_numpy(dtype=np.float64) # type: ignore[assignment]
        lows: NDArray[np.float64] = g[low_col].to_numpy(dtype=np.float64) # type: ignore[assignment]
        sl_p: NDArray[np.float64] = g[sl_col].to_numpy(dtype=np.float64) # type: ignore[assignment]
        tp_p: NDArray[np.float64] = g[tp_col].to_numpy(dtype=np.float64) # type: ignore[assignment]
        for i in range(len(g)):
            start = i + lag_bars
            if start >= len(g):
                break
            entry = closes[i]
            sl = sl_p[i]
            tp = tp_p[i]
            long_tp = entry * (1 + tp)
            long_sl = entry * (1 - sl)
            short_tp = entry * (1 - tp)
            short_sl = entry * (1 + sl)
            j_end = min(len(g), start + horizon_bars)
            h_seg = highs[start:j_end]
            l_seg = lows[start:j_end]
            hits: list[tuple[str, int]] = []
            if np.any(h_seg >= long_tp): hits.append(("BUY_TP", int(np.argmax(h_seg >= long_tp))))
            if np.any(l_seg <= long_sl): hits.append(("BUY_SL", int(np.argmax(l_seg <= long_sl))))
            if np.any(l_seg <= short_tp): hits.append(("SELL_TP", int(np.argmax(l_seg <= short_tp))))
            if np.any(h_seg >= short_sl): hits.append(("SELL_SL", int(np.argmax(h_seg >= short_sl))))

            if not hits:
                continue

            evt, t = min(hits, key=lambda x: x[1])
            global_i = idxs[i]
            signal[global_i] = 1 if evt.startswith("BUY") else 2
            success[global_i] = 1 if evt.endswith("TP") else 0
            t_first[global_i] = t + 1

    out["signal"] = signal
    out["success"] = success
    out["t_first"] = t_first
    return out
