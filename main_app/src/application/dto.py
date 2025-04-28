from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class LoginDto:
    username: str
    password: str


@dataclass(slots=True, frozen=True)
class UserDTO:
    id: int
    username: str


@dataclass(slots=True, frozen=True)
class OkxWebSocketConfigDTO:
    conn_name: str
    user_id: int
    instType: str
    account: bool
    positions: bool
    liq_warning: bool
    api_key: str
    secret_key: str
    passphrase: str


@dataclass(slots=True, frozen=True)
class UserSignupDTO:
    username: str
    password: str