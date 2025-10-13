# ai/src/preprocess/adapters/labeling_adapter.py

import pandas as pd
from preprocess.labeling import label_first_touch

class LabelingAdapter:
    """
    Adapter for applying event-based labeling to financial time series.

    Uses the `label_first_touch` strategy to assign binary or multi-class labels
    based on future price movements within a defined horizon.

    Parameters:
        asset_col (str): Column name identifying the asset (default: "asset_id").
        lag_bars (int): Number of bars to lag before evaluating future movement.
        horizon_bars (int): Number of bars ahead to monitor for label assignment.
    """

    def __init__(
        self, 
        asset_col: str = "asset_id", 
        lag_bars: int = 1, 
        horizon_bars: int = 64
    ) -> None:
        """
        Initializes the LabelingAdapter with labeling parameters.

        Parameters:
            asset_col (str): Asset identifier column.
            lag_bars (int): Number of bars to lag before label evaluation.
            horizon_bars (int): Number of bars ahead to monitor for first-touch labeling.
        """
        self.asset_col = asset_col
        self.lag_bars = lag_bars
        self.horizon_bars = horizon_bars

    def label(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies first-touch labeling to the input dataframe.

        Delegates to `label_first_touch`, which assigns labels based on
        whether future price reaches predefined thresholds within the horizon.

        Parameters:
            df (pd.DataFrame): Input dataframe containing asset and price columns.

        Returns:
            pd.DataFrame: Dataframe with assigned labels.
        """
        return label_first_touch(
            df,
            asset_col=self.asset_col,
            lag_bars=self.lag_bars,
            horizon_bars=self.horizon_bars
        )
