from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class GetPriceDataDTO:
    instId: str
    bar: str | None = None
    after: str | None = None
    before: str | None = None
    limit: str | None = None


@dataclass(slots=True, frozen=True)
class GetMarkPriceDTO:
    instType: str
    instId: str | None = None
