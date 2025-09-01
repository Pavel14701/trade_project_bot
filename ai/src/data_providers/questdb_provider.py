from .base import BaseProvider
import pandas as pd
import requests
from typing import Dict, Any

class QuestDBProvider(BaseProvider):
    def __init__(self, host: str) -> None:
        self.host = host.rstrip("/")

    def fetch(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        query = f"""
        SELECT timestamp, open, high, low, close, volume
        FROM market_data
        WHERE symbol = '{symbol}'
            AND timestamp BETWEEN '{start}' AND '{end}'
        ORDER BY timestamp
        """
        url = f"{self.host}/exec"
        response = requests.get(url, params={"query": query})
        response.raise_for_status()
        json_data: Dict[str, Any] = response.json()
        columns = [col["name"] for col in json_data.get("columns", [])]
        rows = json_data.get("dataset", [])
        df = pd.DataFrame(rows, columns=list(columns))
        df["asset_id"] = symbol
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce") #type: ignore
        return df
