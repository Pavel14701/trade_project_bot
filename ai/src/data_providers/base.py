from abc import abstractmethod
from typing import Protocol

import pandas as pd


class BaseProvider(Protocol):
    """
    Interface for financial data providers.

    Implementations must return a DataFrame containing historical time series data
    for a given asset symbol over a specified date range.

    Parameters:
        symbol (str): Asset ticker (e.g., "AAPL", "BTC-USD").
        start (str): Start date in ISO format (inclusive).
        end (str): End date in ISO format (inclusive).

    Returns:
        pd.DataFrame: Time-indexed data with columns 
          such as open, high, low, close, volume.
    """
    @abstractmethod
    def fetch(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        raise NotImplementedError()
