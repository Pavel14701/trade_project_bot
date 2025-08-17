from dataclasses import asdict, dataclass
from typing import Self, Any


@dataclass(slots=True)
class BaseDataClass:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def replace(cls, instance: Self, **kwargs: Any) -> Self:
        return cls(**{**instance.to_dict(), **kwargs})


@dataclass(slots=True)
class WebSocketDM(BaseDataClass):
    user_id: int
    instType: str
    account: bool
    positions: bool
    liq_warning: bool
    api_key: str
    secret_key: str
    passphrase: str
    close: bool = False