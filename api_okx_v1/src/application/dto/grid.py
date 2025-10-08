from dataclasses import dataclass

from api_okx_v1.src.application.dto.base import BaseDataClass


@dataclass(frozen=True, slots=True)
class PlaceGridOrderDTO(BaseDataClass):
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
    spotGridOrder: "SpotGridOrder | None" = None
    contractGridOrder: "ContractGridOrder | None" = None


@dataclass(frozen=True, slots=True)
class PlaceTriggerParams(BaseDataClass):
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
class SpotGridOrder(BaseDataClass):
    quoteSz: str | None = None
    baseSz: str | None = None


@dataclass(frozen=True, slots=True)
class ContractGridOrder(BaseDataClass):
    sz: str
    direction: str
    lever: str
    basePos: bool | None = None
    tpRatio: str | None = None
    slRatio: str | None = None


@dataclass(frozen=True, slots=True)
class AmendGridOrderDTO(BaseDataClass):
    algoId: str
    instId: str
    slTriggerPx: str | None = None
    tpTriggerPx: str | None = None
    tpRatio: str | None = None
    slRatio: str | None = None
    triggerParams: list["AmendTriggerParams"] | None = None


@dataclass(frozen=True, slots=True)
class AmendTriggerParams(BaseDataClass):
    triggerAction: str
    triggerStrategy: str
    triggerPx: str | None = None
    stopType: str | None = None


@dataclass(frozen=True, slots=True)
class StopGridOrderDTO(BaseDataClass):
    algoId: str
    instId: str
    algoOrdType: str
    stopType: str


@dataclass(frozen=True, slots=True)
class CloseContractGridDTO(BaseDataClass):
    algoId: str
    mktClose: bool
    sz: str | None = None
    px: str | None = None


@dataclass(slots=True, frozen=True)
class CancelCloseContractGridDTO(BaseDataClass):
    algoId: str
    ordId: str


@dataclass(slots=True, frozen=True)
class GetGridOrderListDTO(BaseDataClass):
    algoOrdType: str  
    algoId: str | None = None
    instId: str | None = None
    instType: str | None = None
    after: str | None = None
    before: str | None = None
    limit: int | None = None


@dataclass(slots=True, frozen=True)
class GetGridOrderDetailsDTO(BaseDataClass):
    algoOrdType: str
    algoId: str


@dataclass(frozen=True, slots=True)
class GetGridSubOrdersDTO(BaseDataClass):
    algoOrdType: str
    algoId: str | None = None
    instId: str | None = None
    instType: str | None = None
    after: str | None = None
    before: str | None = None
    limit: int | None = None


@dataclass(frozen=True, slots=True)
class ComputeMarginBalanceDTO(BaseDataClass):
    algoId: str
    type: str
    amt: str | None = None


@dataclass(frozen=True, slots=True)
class AdjustMarginBalanceDTO(BaseDataClass):
    algoId: str
    type: str
    amt: str | None = None
    percent: str | None = None


@dataclass(frozen=True, slots=True)
class AddIvestmentDTO(BaseDataClass):
    algoId: str
    amt: str
    allowReinvestProfit: str | None = None


@dataclass(frozen=True, slots=True)
class AiParamsPublicDTO(BaseDataClass):
    algoOrdType: str
    instId: str
    direction: str | None = None
    duration: str | None = None


@dataclass(frozen=True, slots=True)
class ComputeMinInvestmentPublicDTO(BaseDataClass):
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
class InvestmentData(BaseDataClass):
    amt: str
    ccy: str


@dataclass(frozen=True, slots=True)
class RsiBacktestingPublicDTO(BaseDataClass):
    instId: str
    timeframe: str
    thold: str
    triggerCond: str | None = None
    duration: str | None = None


@dataclass(frozen=True, slots=True)
class MaxGridQuantityPublicDTO(BaseDataClass):
    instId:	str	
    runType: str
    algoOrdType: str
    maxPx: str
    minPx: str
    lever: str | None = None