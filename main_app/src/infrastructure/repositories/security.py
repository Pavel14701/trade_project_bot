from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from cryptography.fernet import Fernet

from main_app.src.application.exceptions import InvalidPasswordException
from main_app.src.application.interfaces import IConfigEncryption, ISecurity
from main_app.src.config import SecretConfig
from main_app.src.domain.entities import PasswordDM, SignupPasswordDM, WebSocketDM


class ConfigEncryptionRepo(IConfigEncryption):
    """
    Handles encryption and decryption of 
    sensitive WebSocket configuration data.
    """

    def __init__(self, cipher: Fernet) -> None:
        """
        Initializes the class with 
        an encryption handler.
        """
        self._cipher = cipher

    async def encrypt(self, model: WebSocketDM) -> WebSocketDM:
        """
        Encrypts API keys, secret keys, and
        passphrases, returning a new 
        WebSocketDM instance.
        """
        return WebSocketDM.replace(
            model,
            api_key=self._cipher.encrypt(model.api_key.encode()).decode(),
            secret_key=self._cipher.encrypt(model.secret_key.encode()).decode(),
            passphrase=self._cipher.encrypt(model.passphrase.encode()).decode()
        )

    async def decrypt(self, model: WebSocketDM) -> WebSocketDM:
        """
        Decrypts API keys, secret keys, and
        passphrases, returning a new 
        WebSocketDM instance.
        """
        try:
            return WebSocketDM.replace(
                model,
                api_key=self._cipher.decrypt(model.api_key.encode()).decode(),
                secret_key=self._cipher.decrypt(model.secret_key.encode()).decode(),
                passphrase=self._cipher.decrypt(model.passphrase.encode()).decode()
            )
        except Exception as e:
            raise ValueError(f"Decryption error: {e}") from e


class SecurityRepo(ISecurity):
    """
    Handles password hashing 
    and verification using Argon2.
    """

    def __init__(
        self,
        password_hasher: PasswordHasher,
        app_config: SecretConfig 
    ) -> None:
        """
        Initializes the class with a password 
        hasher and application configuration.
        """
        self._password_hasher = password_hasher
        self._app_config = app_config

    async def verify_password(self, model: PasswordDM) -> None:
        """
        Verifies the provided password using 
        salt and pepper for added security.
        """
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
        except (
            VerifyMismatchError, VerificationError, InvalidHashError
        ) as e:
            raise InvalidPasswordException() from e

    async def hash_password(self, model: SignupPasswordDM) -> PasswordDM:
        """
        Hashes the user's password using
        salt and pepper, returning a new 
        PasswordDM instance.
        """
        salted_password = "{salt}{password}{pepper}".format(
            salt=model.salt,
            password=model.password,
            pepper=self._app_config.pepper
        )
        hashed_password = self._password_hasher.hash(salted_password)
        return PasswordDM(model.salt, model.password, hashed_password)
