from pydantic import BaseModel, Field, field_validator


class OkxWebSocketConfigRequest(BaseModel):
    conn_name: str = Field(
        max_length=255,
        description="Name for connection"
    )
    instType: str = Field(
        default="ANY", 
        max_length=10, 
        description="Instrument type for subscription"
    )
    account: bool = Field(
        default=False, 
        description="Receive account updates"
    )
    positions: bool = Field(
        default=True, 
        description="Receive position updates"
    )
    liq_warning: bool = Field(
        default=False, 
        description="Receive liquidation warnings"
    )
    api_key: str = Field(
        min_length=1, 
        max_length=255, 
        description="API key"
    )
    secret_key: str = Field(
        min_length=1, 
        max_length=255, 
        description="API secret key"
    )
    passphrase: str = Field(
        min_length=1, 
        max_length=255, 
        description="API passphrase"
    )


class UserLoginRequest(BaseModel):
    username: str = Field(
        min_length=3, 
        max_length=255, 
        description="User's unique username"
    )
    password: str = Field(
        min_length=12, 
        max_length=60, 
        description="User's secure password."
        )


class UserSignupRequest(UserLoginRequest):
    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if not any(map(str.isupper, value)) \
        or not any(map(str.isdigit, value)) \
        or all(map(str.isalnum, value)):
            raise ValueError("""
                Password must contain at least one 
                uppercase letter, one digit, and 
                one special character
            """)
        return value