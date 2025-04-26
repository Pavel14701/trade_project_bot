from abc import abstractmethod
from typing import Protocol 

from main_app.src.application.exceptions import UserAlreadyExistsError, UserGetManyConnections
from main_app.src.domain.entities import (
    PasswordDM,
    SignupPasswordDM, 
    UserDm, 
    UserPasswordDM,
    UserSignupDM,
    WebSocketDM
)


class IUser(Protocol):
    @abstractmethod
    async def get_password(self, username: str) -> UserPasswordDM:
        ...

    @abstractmethod
    async def signup(self, singup_dm: UserSignupDM) -> None:
        ...

    @abstractmethod
    async def get_current_user(self, user_id: int) -> UserDm: 
        ...


class ISecurity(Protocol):
    @abstractmethod
    async def verify_password(self, password: PasswordDM) -> None: 
        ...

    @abstractmethod
    async def hash_password(self, model: SignupPasswordDM) -> PasswordDM:
        ...


class IOkxListner(Protocol):
    @abstractmethod
    async def save_okx_listner_config(self, config: WebSocketDM) -> None: 
        ...

    @abstractmethod
    async def get_ls_configs(self, user_id: int) -> list[WebSocketDM]: 
        ...


class IConfigEncryption(Protocol):
    @abstractmethod
    async def encrypt(self, model: WebSocketDM) -> WebSocketDM: 
        ...

    @abstractmethod
    async def decrypt(self, model: WebSocketDM) -> WebSocketDM: 
        ...


class ISession(Protocol):
    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def flush(self) -> None:
        ...

    @abstractmethod
    async def rollback(self) -> None:
        ...


class IErrorHandler(Protocol):
    @abstractmethod
    def many_connections(self, error: Exception) -> UserGetManyConnections:
        ...

    @abstractmethod
    def user_already_exists(self, error: Exception) -> UserAlreadyExistsError:
        ...