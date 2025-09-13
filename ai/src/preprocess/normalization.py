import pandas as pd
import numpy as np
from typing import List, Optional


def scale_group(
    g: pd.DataFrame,
    cols: List[str],
    window: int,
    eps: float,
    clip_iqr: Optional[float],
    suffix: str
) -> pd.DataFrame:
    """
    Applies rolling robust scaling to selected columns within a single group.

    For each column, computes rolling median and IQR over a specified window,
    then normalizes values using (x - median) / (IQR + eps). Optionally clips
    extreme values to a fixed range.

    Parameters:
        g (pd.DataFrame): Grouped dataframe (e.g., one asset).
        cols (List[str]): Columns to normalize.
        window (int): Rolling window size.
        eps (float): Small constant to avoid division by zero.
        clip_iqr (Optional[float]): Optional clipping threshold for scaled values.
        suffix (str): Suffix to append to scaled column names.

    Returns:
        pd.DataFrame: Group with added scaled columns.
    """
    for col in cols:
        col_series: pd.Series[float] = g[col].astype(float)
        med: pd.Series[float] = col_series.rolling(window).median().shift(1)  # type: ignore[reportUnknownMemberType]
        q1: pd.Series[float] = col_series.rolling(window).quantile(0.25).shift(1)  # type: ignore[reportUnknownMemberType]
        q3: pd.Series[float] = col_series.rolling(window).quantile(0.75).shift(1)  # type: ignore[reportUnknownMemberType]
        iqr: pd.Series[float] = (q3 - q1).replace(0.0, np.nan)  # type: ignore[reportUnknownMemberType]
        z: pd.Series[float] = (col_series - med) / (iqr + eps)  # type: ignore[reportUnknownMemberType]
        if clip_iqr is not None:
            z = z.clip(lower=-clip_iqr, upper=clip_iqr) # type: ignore[reportUnknownMemberType]
        g[f"{col}{suffix}"] = z
    return g

def rolling_robust_scale_by_asset(
    df: pd.DataFrame,
    cols: List[str],
    asset_col: str,
    window: int = 252,
    eps: float = 1e-6,
    clip_iqr: Optional[float] = 3.0,
    suffix: str = "_scaled"
) -> pd.DataFrame:
    """
    Applies rolling robust scaling to numeric features per asset.

    Sorts the dataframe by asset and time index, then applies asset-wise
    normalization using rolling median and IQR. Scaled columns are appended
    with the specified suffix.

    Parameters:
        df (pd.DataFrame): Input dataframe with asset and numeric columns.
        cols (List[str]): Columns to normalize.
        asset_col (str): Column identifying asset groups.
        window (int): Rolling window size (default: 252).
        eps (float): Small constant to avoid division by zero.
        clip_iqr (Optional[float]): Optional clipping threshold (default: 3.0).
        suffix (str): Suffix for scaled column names (default: "_scaled").

    Returns:
        pd.DataFrame: Dataframe with scaled features added.
    """
    out: pd.DataFrame = df.copy()
    index_name: str = out.index.name if isinstance(out.index.name, str) else "index"  # type: ignore[reportUnknownMemberType]
    sort_keys: List[str] = [asset_col, index_name] 
    out = out.sort_values(sort_keys) # type: ignore[reportUnknownMemberType]
    scaled: pd.DataFrame = out.groupby(asset_col, group_keys=False).apply( # type: ignore[reportUnknownMemberType]
        lambda g: scale_group(g, cols, window, eps, clip_iqr, suffix)
    )
    return scaled
