from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserDTO(BaseDTO):
    """DTO для представления данных пользователя"""
    username: str


class WebSocketConfigDTO(BaseDTO):
    """DTO для представления WebSocket конфигурации"""
    user_id: int
    instType: str
    account: bool
    positions: bool
    liq_warning: bool


class UserSecretsDTO(BaseDTO):
    """DTO для представления расшифрованных секретов пользователя"""
    user_id: int
    api_key: str
    secret_key: str
    passphrase: str
