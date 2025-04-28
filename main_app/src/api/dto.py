from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class PriceDataRequestDTO:
    inst_id: str
    _from: datetime | None = None
    to: datetime | None = None
    limit: int | None = None
    timeframe: str
    is_demo: bool


@dataclass(slots=True, frozen=True)
class MarkPriceRequestDto:
    inst_type: str
    inst_id: str | None = None