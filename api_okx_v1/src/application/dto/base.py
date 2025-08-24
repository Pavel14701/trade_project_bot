from typing import Any
from dataclasses import dataclass, asdict


@dataclass(slots=True, frozen=True)
class BaseDataClass:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class SecretDTO(BaseDataClass):
    api_key: str
    secret_key: str
    passphrase: str