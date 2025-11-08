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
class SecretDTO(BaseDataClass):
    api_key: str
    secret_key: str
    passphrase: str