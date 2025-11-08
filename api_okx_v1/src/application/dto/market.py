from dataclasses import dataclass

from api_okx_v1.src.application.dto.base import BaseDataClass


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
    instFamily: str | None = None
    instId: str | None = None