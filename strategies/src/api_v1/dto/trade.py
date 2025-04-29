from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class GetBalanceDTO:
    instType: str | None = None
    instId: str | None = None
    posId: str | None = None


@dataclass(slots=True, frozen=True)
class SetLeverageDTO:
    instId: str
    ccy: str
    lever: str
    mgnMode: str
    posSide: str


@dataclass(slots=True, frozen=True)
class GetLeverageDTO:
    instId: str
    ccy: str
    mgn_mode: str


@dataclass(slots=True, frozen=True)
class PlaceOrderDTO:
    instId: str
    tdMode: str
    side: str
    orderType: str
    sz: str
    px: str
    ccy: str | None = None
    clOrdId: str | None = None
    tag: str | None = None
    posSide: str | None = None
    pxUsd: str | None = None
    pxVol: str | None = None
    reduceOnly: str | None = None
    tgtCcy: str | None = None
    banAmend: bool | None = None
    stpMode: str | None = None
    attachAlgoOrds: list["AttachAlgoOrds"] | None = None


@dataclass(slots=True, frozen=True)
class AmendOrderDTO:
    instId: str
    cxlOnFail: bool | None = None
    ordId: str | None = None
    clOrdId: str | None = None
    reqId: str | None = None
    newSz: str | None = None
    newPx: str | None = None
    newPxUsd: str | None = None
    newPxVol: str | None = None
    attachAlgoOrds: list["AttachAlgoOrds"]


@dataclass(slots=True, frozen=True)
class AttachAlgoOrds:
    attachAlgoClOrdId: str | None = None 
    tpTriggerPx: str | None = None
    tpOrdPx: str | None = None
    tpOrdKind: str | None = None
    slTriggerPx: str | None = None
    slOrdPx: str | None = None
    tpTriggerPxType: str | None = None
    slTriggerPxType: str | None = None
    sz: str| None = None
    amendPxOnTriggerType: str | None = None


@dataclass(slots=True, frozen=True)
class CancelOrerDTO:
    instId: str
    ordId: str | None = None
    clOrdId: str | None = None


@dataclass(frozen=True, slots=True)
class ClosePositionsDTO:
    instId: str
    posSide: str | None = None
    mgnMode: str
    ccy: str | None = None
    autoCxl: bool | None = None
    clOrdId: str | None = None
    tag: str | None = None


@dataclass(frozen=True, slots=True)
class GetOrderDetailsDTO:
    instId: str
    ordId: str | None = None
    clOrdId: str | None = None


@dataclass(frozen=True, slots=True)
class GetOrderListDTO:
    instType: str | None = None
    uly: str | None = None
    instFamily: str | None = None
    instId: str | None = None
    ordType: str | None = None
    state: str | None = None
    after: str | None = None
    before: str | None = None
    limit: int | None = None