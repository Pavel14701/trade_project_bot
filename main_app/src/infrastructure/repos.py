from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from main_app.src.application.interfaces import (
    IErrorHandler,
    IUser
)
from main_app.src.domain.entities import (
    UserDm, 
    UserPasswordDM,
    UserSignupDM, 
    WebSocketDM
)
from main_app.src.application.exceptions import (
    UserAlreadyExistsError,
    UserGetManyConnections,
    UserNotFoundException
)
from main_app.src.infrastructure.models import (
    OkxListenerConfig, 
    User
)


class UserRepo(IUser):
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def get_password(
        self, 
        username: str
    ) -> UserPasswordDM:
        result = await self._session.execute(
            select(User).where(
                User.username == username
        ))
        if user := result.scalars().first():
            return UserPasswordDM(**user)
        raise UserNotFoundException()

    async def get_current_user(
        self, 
        user_id: int
    ) -> UserDm:
        if user := await self._session.get(User, user_id):
            return UserDm(**user)
        raise UserNotFoundException()

    async def save_okx_listner_config(
        self, 
        config: WebSocketDM
    ) -> None:
        config_model = OkxListenerConfig()
        config_model.user_id = config.user_id
        config_model.instType = config.instType
        config_model.account = config.account
        config_model.positions = config.positions
        config_model.liq_warning = config.liq_warning
        config_model.api_key = config.api_key
        config_model.secret_key = config.secret_key
        config_model.passphrase = config.passphrase
        self._session.add(config_model)

    async def get_okx_listner_configs(
        self, 
        user_id: int
    ) -> list[WebSocketDM]:
        statement = select(OkxListenerConfig).where(
            OkxListenerConfig.user_id == user_id
        )
        _results = await self._session.execute(statement)
        results = _results.scalars().all()
        return [WebSocketDM(**result) for result in results]

    async def signup(self, signup_dm: UserSignupDM) -> None:
        model = User()
        model.hashed_password = signup_dm.hashed_password
        model.username = signup_dm.username
        model.salt = signup_dm.salt
        self._session.add(model)


# TODO сделать ExceptionHandlersRepo на типах 

class ExceptionHandlersRepo(IErrorHandler):
    def user_already_exists(
        self, 
        error: Exception
    ) -> (UserAlreadyExistsError | Exception):
        return UserAlreadyExistsError() if isinstance(
            error, IntegrityError
        ) else error

    def many_connections(
        self, 
        error: Exception
    ) -> (UserGetManyConnections | Exception):
        return UserGetManyConnections() if isinstance(
            error, IntegrityError
        ) else error
