from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class PlaceGridOrderDTO:
    instId: str
    algoOrdType: str
    maxPx: str
    minPx: str 
    gridNum: str
    runType: str | None = None
    tpTriggerPx: str | None = None
    slTriggerPx: str | None = None
    algoClOrdId: str | None = None
    tag: str | None = None
    profitSharingRatio: str | None = None
    triggerParams: list["PlaceTriggerParams"] | None = None
    spotGridOrder: "SpotGridOrder" | None = None
    contractGridOrder: "ContractGridOrder" | None = None


@dataclass(frozen=True, slots=True)
class PlaceTriggerParams:
    triggerAction: str
    triggerStrategy: str
    delaySeconds: str | None = None
    timeframe: str | None = None
    thold: str | None = None
    triggerCond: str | None = None
    timePeriod: str | None = None
    triggerPx: str | None = None
    stopType: str | None = None


@dataclass(frozen=True, slots=True)
class SpotGridOrder:
    quoteSz: str | None = None
    baseSz: str | None = None


@dataclass(frozen=True, slots=True)
class ContractGridOrder:
    sz: str
    direction: str
    lever: str
    basePos: bool | None = None
    tpRatio: str | None = None
    slRatio: str | None = None


@dataclass(frozen=True, slots=True)
class AmendGridOrderDTO:
    algoId: str
    instId: str
    slTriggerPx: str | None = None
    tpTriggerPx: str | None = None
    tpRatio: str | None = None
    slRatio: str | None = None
    triggerParams: list["AmendTriggerParams"] | None = None


@dataclass(frozen=True, slots=True)
class AmendTriggerParams:
    triggerAction: str
    triggerStrategy: str
    triggerPx: str | None = None
    stopType: str | None = None


@dataclass(frozen=True, slots=True)
class StopGridOrderDTO:
    algoId: str
    instId: str
    algoOrdType: str
    stopType: str