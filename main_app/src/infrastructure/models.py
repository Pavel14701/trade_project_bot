from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet
import secrets
from sqlalchemy import String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship

from main_app.src.config import AppConfig


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    _hashed_password: Mapped[str] = mapped_column("hashed_password", String, nullable=False)
    salt: Mapped[str] = mapped_column(String, nullable=False)

    def __init__(
        self, 
        app_config: AppConfig,
        password_hasher: PasswordHasher,
    ) -> None:
        self._app_config = app_config
        self._password_hasher = password_hasher

    @property
    def password(self) -> str:
        return self._hashed_password

    @password.setter
    def password(self, value: str) -> None:
        """Автоматически хеширует пароль при записи."""
        self.salt = secrets.token_hex(8)
        salted_password = f"{self.salt}{value}{self._app_config.pepper}"
        self._hashed_password = self._password_hasher.hash(salted_password)

    def verify_password(self, password: str) -> bool:
        """Проверяет введённый пароль, используя Salt и Pepper."""
        try:
            salted_password = f"{self.salt}{password}{self._app_config.pepper}"
            return self._password_hasher.verify(self._hashed_password, salted_password)
        except VerifyMismatchError:
            return False


class WebSocketConfig(Base):
    __tablename__ = "websocket_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    instType: Mapped[str] = mapped_column(String, default="ANY")
    account: Mapped[bool] = mapped_column(Boolean, default=False)
    positions: Mapped[bool] = mapped_column(Boolean, default=True)
    liq_warning: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", back_populates="websocket_configs")


class UserSecrets(Base):
    __tablename__ = "user_secrets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    _api_key: Mapped[str] = mapped_column("encrypted_api_key", String, nullable=False)
    _secret_key: Mapped[str] = mapped_column("encrypted_secret_key", String, nullable=False)
    _passphrase: Mapped[str] = mapped_column("encrypted_passphrase", String, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="secrets")

    def __init__(self, cipher: Fernet) -> None:
        self._cipher = cipher

    @property
    def api_key(self) -> str:
        return self._cipher.decrypt(self._api_key.encode()).decode()

    @api_key.setter
    def api_key(self, value: str) -> None:
        """Автоматически шифрует API-ключ при записи в атрибут."""
        self._api_key = self._cipher.encrypt(value.encode()).decode()

    @property
    def secret_key(self) -> str:
        return self._cipher.decrypt(self._secret_key.encode()).decode()

    @secret_key.setter
    def secret_key(self, value: str) -> None:
        """Автоматически шифрует секретный ключ при записи."""
        self._secret_key = self._cipher.encrypt(value.encode()).decode()

    @property
    def passphrase(self) -> str:
        return self._cipher.decrypt(self._passphrase.encode()).decode()

    @passphrase.setter
    def passphrase(self, value: str) -> None:
        """Автоматически шифрует passphrase при записи."""
        self._passphrase = self._cipher.encrypt(value.encode()).decode()