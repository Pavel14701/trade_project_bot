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


@dataclass(frozen=True, slots=True)
class CloseContractGridDTO:
    algoId: str
    mktClose: bool
    sz: str | None = None
    px: str | None = None


@dataclass(slots=True, frozen=True)
class CancelCloseContractGridDTO:
    algoId: str
    ordId: str


@dataclass(slots=True, frozen=True)
class GetGridOrderListDTO:
    algoOrdType: str  
    algoId: str | None = None
    instId: str | None = None
    instType: str | None = None
    after: str | None = None
    before: str | None = None
    limit: int | None = None


@dataclass(slots=True, frozen=True)
class GetGridOrderDetailsDTO:
    algoOrdType: str
    algoId: str


@dataclass(frozen=True, slots=True)
class GetGridSubOrersDTO:
    algoOrdType: str
    algoId: str | None = None
    instId: str | None = None
    instType: str | None = None
    after: str | None = None
    before: str | None = None
    limit: int | None = None


@dataclass(frozen=True, slots=True)
class ComputeMarginBalanceDTO:
    algoId: str
    type: str
    amt: str | None = None


@dataclass(frozen=True, slots=True)
class AdjustMarginBalanceDTO:
    algoId: str
    type: str
    amt: str | None = None
    percent: str | None = None


@dataclass(frozen=True, slots=True)
class AddIvestmentDTO:
    algoId: str
    amt: str
    allowReinvestProfit: str | None = None


@dataclass(frozen=True, slots=True)
class AiParamsPublicDTO:
    algoOrdType: str
    instId: str
    direction: str | None = None
    duration: str | None = None


@dataclass(frozen=True, slots=True)
class ComputeMinInvestmentPublicDTO:
    instId: str
    algoOrdType: str
    maxPx: str
    minPx: str
    gridNum: str
    runType: str
    direction: str | None = None
    lever: str | None = None
    basePos: bool | None = None
    investmentType: str | None = None
    triggerStrategy: str | None = None
    investmentData: list["InvestmentData"] | None = None


@dataclass(frozen=True, slots=True)
class InvestmentData:
    amt: str
    ccy: str


@dataclass(frozen=True, slots=True)
class RsiBacktestingPublicDTO:
    instId: str
    timeframe: str
    thold: str
    triggerCond: str | None = None
    duration: str | None = None



@dataclass(frozen=True, slots=True)
class MaxGridQuantityPublicDTO:
    instId:	str	
    runType: str
    algoOrdType: str
    maxPx: str
    minPx: str
    lever: str | None = None