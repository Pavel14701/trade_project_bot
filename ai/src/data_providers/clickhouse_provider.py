# src/data_providers/clickhouse_provider.py

from .base import BaseProvider
import pandas as pd
from sqlalchemy import create_engine, text
from typing import Optional

class ClickHouseProvider(BaseProvider):
    """
    ClickHouse-backed implementation of the BaseProvider interface.

    Connects to a ClickHouse database and retrieves historical market data
    for a given asset symbol over a specified date range.

    Parameters:
        host (str): Hostname of the ClickHouse server.
        database (str): Target database name.
        user (str): Username for authentication.
        password (Optional[str]): Password for authentication (if required).
        port (int): Port number for the ClickHouse native protocol.

    Methods:
        fetch(symbol, start, end):
            Executes a parameterized SQL query to retrieve OHLCV data
            for the given symbol between start and end dates (inclusive).
            Returns a DataFrame indexed by timestamp, with asset_id attached.
    """
    def __init__(
        self,
        host: str = "localhost",
        database: str = "default",
        user: str = "default",
        password: Optional[str] = None,
        port: int = 9000
    ) -> None:
        """
        Initializes a ClickHouseProvider instance with connection parameters.

        Constructs a SQLAlchemy engine using the native ClickHouse protocol.

        Parameters:
            host (str): Hostname of the ClickHouse server.
            database (str): Name of the target database.
            user (str): Username for authentication.
            password (Optional[str]): Password for authentication (if required).
            port (int): Port number for the ClickHouse native protocol.
        """
        if password is not None:
            uri = f"clickhouse+native://{user}:{password}@{host}:{port}/{database}"
        else:
            uri = f"clickhouse+native://{user}@{host}:{port}/{database}"
        self.engine = create_engine(uri)

    def fetch(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """
        Retrieves historical OHLCV data for a given asset symbol and date range.

        Executes a parameterized SQL query against the `market_data` table,
        filtering by symbol and timestamp range. The result is returned as a
        pandas DataFrame with datetime-indexed rows and an added `asset_id` column.

        Parameters:
            symbol (str): Asset ticker (e.g., "AAPL", "BTC-USD").
            start (str): Start date in ISO format (inclusive).
            end (str): End date in ISO format (inclusive).

        Returns:
            pd.DataFrame: DataFrame containing columns:
                - timestamp (datetime)
                - open, high, low, close, volume (float)
                - asset_id (str)
        """
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
