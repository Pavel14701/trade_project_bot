from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenRegister(BaseModel):
    user_id: int
    api_key: str
    secret_key: str