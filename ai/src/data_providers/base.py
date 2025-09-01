# src/data_providers/base.py

from abc import abstractmethod
from typing import Protocol
import pandas as pd

class BaseProvider(Protocol):
    @abstractmethod
    def fetch(self, symbol: str, start: str, end: str) -> pd.DataFrame: 
        raise NotImplementedError()
