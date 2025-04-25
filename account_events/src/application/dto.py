from dataclasses import dataclass

@dataclass(slots=True)
class WebSocketDTO:
    user_id: int
    instType: str
    account: bool
    positions: bool
    liq_warning: bool
    api_key: str
    secret_key: str
    passphrase: str
    close: bool