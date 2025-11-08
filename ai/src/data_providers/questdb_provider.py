from typing import Any, Dict

import pandas as pd
import requests

from .base import BaseProvider


class QuestDBProvider(BaseProvider):
    """
    QuestDB-backed implementation of the BaseProvider interface.

    Sends SQL queries over HTTP to a QuestDB instance and retrieves historical
    OHLCV market data for a specified asset symbol and time range.

    Parameters:
        host (str): Base URL of the QuestDB HTTP endpoint (e.g., "http://localhost:9000").
        timeout (float): Request timeout in seconds.
    """

    def __init__(self, host: str, timeout: float = 30.0) -> None:
        """
        Initializes the QuestDBProvider with connection settings.

        Strips trailing slashes from the host URL and sets the request timeout.

        Parameters:
            host (str): Base URL of the QuestDB HTTP endpoint.
            timeout (float): Timeout for HTTP requests in seconds.
        """
        self.host = host.rstrip("/")
        self.timeout = timeout

    def fetch(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """
        Executes a SQL query against QuestDB to retrieve OHLCV data.

        Sends a parameterized query via HTTP GET to the QuestDB `/exec` endpoint.
        If the request fails, returns an empty DataFrame with expected columns.

        Parameters:
            symbol (str): Asset ticker (e.g., "AAPL", "BTC-USD").
            start (str): Start date in ISO format (inclusive).
            end (str): End date in ISO format (inclusive).

        Returns:
            pd.DataFrame: DataFrame with columns:
                - timestamp (datetime)
                - open, high, low, close, volume (float)
                - asset_id (str)
        """
        query = f"""
        SELECT timestamp, open, high, low, close, volume
        FROM market_data
        WHERE symbol = '{symbol}'
            AND timestamp BETWEEN '{start}' AND '{end}'
        ORDER BY timestamp
        """
        url = f"{self.host}/exec"
        try:
            response = requests.get(url, params={"query": query}, timeout=self.timeout)
            response.raise_for_status()
            json_data: Dict[str, Any] = response.json()
        except requests.RequestException:
            return self._empty_frame(symbol)

        columns = [col["name"] for col in json_data.get("columns", [])]
        rows = json_data.get("dataset", [])
        df = pd.DataFrame(rows, columns=columns)
        df["asset_id"] = symbol
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")  # type: ignore
        return df

    def _empty_frame(self, symbol: str) -> pd.DataFrame:
        """
        Constructs an empty DataFrame with the expected schema.

        Used as a fallback when the data fetch fails due to network or query errors.

        Parameters:
            symbol (str): Asset ticker to assign in the `asset_id` column.

        Returns:
            pd.DataFrame: Empty DataFrame with columns:
                - timestamp, open, high, low, close, volume, asset_id
        """
        return pd.DataFrame(columns=[  # type: ignore
            "timestamp", "open", "high", "low", "close", "volume", "asset_id"
        ]).assign(asset_id=symbol)
