from typing import Self
from dataclasses import dataclass, asdict

@dataclass(slots=True)
class BaseDataClass:
    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def replace(cls, instance: Self, **kwargs) -> Self:
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