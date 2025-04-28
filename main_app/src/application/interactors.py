from dataclasses import asdict
import secrets

from main_app.src.application.dto import (
    LoginDto, 
    OkxWebSocketConfigDTO, 
    UserDTO,
    UserSignupDTO
)
from main_app.src.application.interfaces import (
    IErrorHandler,
    ISession,
    IUser,
    ISecurity,
    IConfigEncryption,
    IOkxListner
)
from main_app.src.domain.entities import (
    PasswordDM,
    SignupPasswordDM,
    UserSignupDM, 
    WebSocketDM
)
from main_app.src.application.exceptions import (
    UserAlreadyExistsError,
    UserGetManyConnections
)


class LoginInteractor:
    def __init__(
        self,
        user_repo: IUser,
        security_repo: ISecurity
    ) -> None:
        self._user_repo = user_repo
        self._security_repo = security_repo

    async def __call__(self, dto: LoginDto) -> int:
        user_dm = await self._user_repo.get_password(dto.username)
        password_dm = PasswordDM(
            salt=user_dm.salt,
            password=dto.password,
            hashed_password=user_dm.hashed_password
        )
        await self._security_repo.verify_password(password_dm)
        return user_dm.id


class GetUserInteractor:
    def __init__(
        self,
        user_repo: IUser
    ) -> None:
        self._user_repo = user_repo

    async def __call__(self, user_id: int) -> UserDTO:
        user = await self._user_repo.get_current_user(user_id)
        return UserDTO(**asdict(user))


class SaveOkxListnerConfigInteractor:
    def __init__(
        self,
        session: ISession,
        listner_repo: IOkxListner,
        encryptor: IConfigEncryption,
        exc_handler: IErrorHandler
    ) -> None:
        self._session = session
        self._listner_repo = listner_repo
        self._encryptor = encryptor
        self._exc_handler = exc_handler

    async def __call__(self, dto: OkxWebSocketConfigDTO) -> None:
        # sourcery skip: raise-from-previous-error
        try:
            config_dm = WebSocketDM(**asdict(dto))
            encrypted_config_dm = await self._encryptor.encrypt(
                model=config_dm
            )
            await self._listner_repo.save_okx_listner_config(
                config=encrypted_config_dm
            )    
            await self._session.commit()
        except Exception as e:
            raise self._exc_handler.handle_error(
                e, UserGetManyConnections
            )


class GetOkxListnerConfigsInteractor:
    def __init__(
        self,
        listner_repo: IOkxListner,
        encryptor: IConfigEncryption
    ) -> None:
        self._listner_repo = listner_repo
        self._encryptor = encryptor

    async def __call__(
            self, 
            user_id: int
    ) -> list[OkxWebSocketConfigDTO]:
        encrypt_configs = await self._listner_repo.get_ls_configs(
            user_id=user_id
        )
        decrypt_configs = [
            await self._encryptor.decrypt(config) 
            for config in encrypt_configs
        ]
        return [
            OkxWebSocketConfigDTO(**config.to_dict()) 
            for config in decrypt_configs
        ]


class SignupInteractor:
    def __init__(
        self,
        session: ISession,
        security: ISecurity,
        user_repo: IUser,
        exc_handler: IErrorHandler 
    ) -> None:
        self._session = session
        self._security = security
        self._user_repo = user_repo
        self._exc_handler = exc_handler

    async def __call__(self, dto: UserSignupDTO) -> UserDTO:
        # sourcery skip: raise-from-previous-error
        try:
            password_input_model = SignupPasswordDM(
                salt=secrets.token_hex(8),
                password=dto.password
            )
            password_model = await self._security.hash_password(
                model=password_input_model
            )
            await self._user_repo.signup(UserSignupDM(
                username=dto.username,
                hashed_password=password_model.hashed_password,
                salt=password_model.salt
            ))
            await self._session.commit()
        except Exception as e:
            raise self._exc_handler.handle_error(
                e, UserAlreadyExistsError
            )
