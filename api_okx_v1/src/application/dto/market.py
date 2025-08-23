from typing import Any
from dataclasses import dataclass, asdict

@dataclass(slots=True, frozen=True)
class BaseDataClass:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(slots=True, frozen=True)
class GetPriceDataDTO(BaseDataClass):
    instId: str
    bar: str | None = None
    after: str | None = None
    before: str | None = None
    limit: str | None = None


@dataclass(slots=True, frozen=True)
class GetMarketPriceDTO(BaseDataClass):
    instType: str
    instId: str | None = None

@dataclass(slots=True, frozen=True)
class GetInstrumentsDTO(BaseDataClass):
    instType: str
    instFamily: str|None = None
    instId: str|None = None