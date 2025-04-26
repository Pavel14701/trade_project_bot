from argon2 import PasswordHasher
from argon2.exceptions import (
    VerifyMismatchError, 
    VerificationError, 
    InvalidHashError
)
from cryptography.fernet import Fernet

from main_app.src.application.interfaces import ConfigEncryption, VerifyPassword
from main_app.src.application.exceptions import InvalidPasswordException 
from main_app.src.config import SecretConfig
from main_app.src.domain.entities import PasswordDM, SignupPasswordDM, UserPasswordDM, WebSocketDM


def get_cipher(config: SecretConfig) -> Fernet:
    return Fernet(config.config_secret_key)


class ConfigEncryptionGateway(ConfigEncryption):
    def __init__(self, cipher: Fernet) -> None:
        """Инициализация класса с шифровальщиком."""
        self._cipher = cipher

    async def encrypt(self, model: WebSocketDM) -> WebSocketDM:
        """Шифрует API-ключи и пароли, возвращая новый объект."""
        return WebSocketDM.replace(
            model,
            api_key=self._cipher.encrypt(model.api_key.encode()).decode(),
            secret_key=self._cipher.encrypt(model.secret_key.encode()).decode(),
            passphrase=self._cipher.encrypt(model.passphrase.encode()).decode()
        )

    async def decrypt(self, model: WebSocketDM) -> WebSocketDM:
        """Расшифровывает API-ключи и пароли, возвращая новый объект."""
        try:
            return WebSocketDM.replace(
                model,
                api_key=self._cipher.decrypt(model.api_key.encode()).decode(),
                secret_key=self._cipher.decrypt(model.secret_key.encode()).decode(),
                passphrase=self._cipher.decrypt(model.passphrase.encode()).decode()
            )
        except Exception as e:
            raise ValueError(f"Ошибка дешифрования: {e}") from e


class SecurityGateways(VerifyPassword):
    def __init__(
        self,
        password_hasher: PasswordHasher,
        app_config: SecretConfig 
    ) -> None:
        self._password_hasher = password_hasher
        self._app_config = app_config

    async def verify_password(self, model: PasswordDM) -> None:
        """Проверяет введённый пароль, используя Salt и Pepper."""
        try:
            salted_password = "{salt}{password}{pepper}".format(
                salt=model.salt,
                password=model.password,
                pepper=self._app_config.pepper
            )
            self._password_hasher.verify(
                hash=model.hashed_password, 
                password=salted_password
            )
        except (VerifyMismatchError, VerificationError, InvalidHashError) as e:
            raise InvalidPasswordException() from e

    async def hash_password(self, model: SignupPasswordDM) -> PasswordDM:
        salted_password = "{salt}{password}{pepper}".format(
            salt=model.salt,
            password=model.password,
            pepper=self._app_config.pepper
        )
        hashed_password = self._password_hasher.hash(salted_password)
        return PasswordDM(model.salt, model.password, hashed_password)