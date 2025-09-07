import pandas as pd
from typing import List
from preprocess.normalization import rolling_robust_scale_by_asset

class FeatureAdapter:
    def __init__(self, num_cols: List[str], asset_col: str = "asset_id", window: int = 252) -> None:
        self.num_cols = num_cols
        self.asset_col = asset_col
        self.window = window

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return rolling_robust_scale_by_asset(df, self.num_cols, asset_col=self.asset_col, window=self.window)
