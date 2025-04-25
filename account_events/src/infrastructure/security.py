from cryptography.fernet import Fernet

from account_events.src.application.interfaces import IConfigEncryption
from account_events.src.config import SecretConfig
from account_events.src.domain.entities import WebSocketDM


def get_cipher(config: SecretConfig) -> Fernet:
    return Fernet(config.config_secret_key)


class ConfigEncryptionGateway(IConfigEncryption):
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
            raise ValueError(f"Ошибка дешифрования: {e}")
