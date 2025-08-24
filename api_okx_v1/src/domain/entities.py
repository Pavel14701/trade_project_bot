from dataclasses import asdict, dataclass
from typing import Any, Self


@dataclass(slots=True, frozen=True)
class BaseDataClass:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def replace(cls, instance: Self, **kwargs: Any) -> Self:
        return cls(**{**instance.to_dict(), **kwargs})


@dataclass(slots=True, frozen=True)
class SecretConfigDM(BaseDataClass):
    user_id: int
    api_key: str
    secret_key: str
    passphrase: str


@dataclass(slots=True)
class SignatureDM:
    secret_key: str 
    method: str
    request_path: str 
    body: str = ''