from .base import BaseProvider
import pandas as pd
import requests
from typing import Dict, Any

class QuestDBProvider(BaseProvider):
    def __init__(self, host: str, timeout: float = 30.0) -> None:
        self.host = host.rstrip("/")
        self.timeout = timeout

    def fetch(self, symbol: str, start: str, end: str) -> pd.DataFrame:
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
        return pd.DataFrame(columns=[ # type: ignore
            "timestamp", "open", "high", "low", "close", "volume", "asset_id"
        ]).assign(asset_id=symbol)
