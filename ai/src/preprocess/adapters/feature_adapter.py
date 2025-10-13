# ai/src/preprocess/adapters/feature_adapter.py

import pandas as pd
from typing import List
from preprocess.normalization import rolling_robust_scale_by_asset

class FeatureAdapter:
    """
    Adapter for applying asset-wise robust normalization to numeric features.

    Uses rolling statistics to scale numeric columns independently per asset,
    preserving temporal structure and cross-asset comparability.

    Parameters:
        num_cols (List[str]): List of numeric column names to normalize.
        asset_col (str): Column name identifying the asset (default: "asset_id").
        window (int): Rolling window size used for robust scaling (default: 252).
    """
    def __init__(
        self, num_cols: List[str], 
        asset_col: str = "asset_id", 
        window: int = 252
    ) -> None:
        """
        Initializes the FeatureAdapter with normalization parameters.

        Parameters:
            num_cols (List[str]): Columns to normalize.
            asset_col (str): Asset identifier column.
            window (int): Rolling window size for scaling.
        """
        self.num_cols = num_cols
        self.asset_col = asset_col
        self.window = window

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies rolling robust scaling to numeric columns per asset.

        Delegates to `rolling_robust_scale_by_asset`, which computes
        asset-wise rolling medians and IQRs for normalization.

        Parameters:
            df (pd.DataFrame): Input dataframe containing numeric and asset columns.

        Returns:
            pd.DataFrame: Transformed dataframe with normalized numeric features.
        """
        return rolling_robust_scale_by_asset(
            df,
            self.num_cols, 
            asset_col=self.asset_col, 
            window=self.window
        )
