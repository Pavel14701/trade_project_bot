import pandas as pd
from preprocess.labeling import label_first_touch

class LabelingAdapter:
    def __init__(self, asset_col: str = "asset_id", lag_bars: int = 1, horizon_bars: int = 64) -> None:
        self.asset_col = asset_col
        self.lag_bars = lag_bars
        self.horizon_bars = horizon_bars

    def label(self, df: pd.DataFrame) -> pd.DataFrame:
        return label_first_touch(
            df,
            asset_col=self.asset_col,
            lag_bars=self.lag_bars,
            horizon_bars=self.horizon_bars
        )
