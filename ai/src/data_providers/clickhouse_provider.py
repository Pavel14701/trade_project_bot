# src/data_providers/clickhouse_provider.py

from .base import BaseProvider
import pandas as pd
from sqlalchemy import create_engine, text
from typing import Optional

class ClickHouseProvider(BaseProvider):
    def __init__(
        self,
        host: str = "localhost",
        database: str = "default",
        user: str = "default",
        password: Optional[str] = None,
        port: int = 9000
    ) -> None:
        uri = f"clickhouse+native://{user}:{password or ''}@{host}:{port}/{database}"
        self.engine = create_engine(uri)

    def fetch(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        query = text("""
            SELECT timestamp, open, high, low, close, volume
            FROM market_data
            WHERE symbol = :symbol
                AND timestamp BETWEEN :start AND :end
            ORDER BY timestamp ASC
        """)
        with self.engine.connect() as conn:
            result = conn.execute(query, {"symbol": symbol, "start": start, "end": end})
            rows = result.fetchall()
            columns = list(result.keys())
        df = pd.DataFrame(rows, columns=columns) 
        df["asset_id"] = symbol
        df["timestamp"] = pd.to_datetime(df["timestamp"]) # type: ignore
        return df
