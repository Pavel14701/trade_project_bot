import hmac
import hashlib
import base64
from datetime import datetime, timezone

from cryptography.fernet import Fernet

from api_okx_v1.src.application.interfaces import ISecurity
from api_okx_v1.src.config import SecretConfig
from api_okx_v1.src.domain.entities import (
    SecretConfigDM,
    SignatureDM
)

def get_cipher(config: SecretConfig) -> Fernet:
    return Fernet(config.config_secret_key)


class SecurityGateway(ISecurity):
    """
    A security utility class for handling encryption, decryption, and API request signing.

    This class provides methods to securely encrypt and decrypt sensitive API credentials 
    using symmetric encryption (Fernet), as well as generate HMAC-based signatures for 
    authenticated requests to the OKX API.

    Attributes:
        _cipher (Fernet): An instance of Fernet used for encryption and decryption.
    """

    def __init__(self, cipher: Fernet) -> None:
        self._cipher = cipher

    async def encrypt(self, model: SecretConfigDM) -> SecretConfigDM:
        """
        Encrypts sensitive fields in a SecretConfigDM model.

        This method takes an object containing API credentials and encrypts each field 
        (API key, secret key, passphrase) using the configured Fernet cipher. It returns 
        a new instance of SecretConfigDM with encrypted values.

        Args:
            model (SecretConfigDM): The original configuration object with plaintext credentials.

        Returns:
            SecretConfigDM: A new configuration object with encrypted credentials.
        """

        return SecretConfigDM.replace(  # type: ignore
            model,
            api_key=self._cipher.encrypt(model.api_key.encode()).decode(),
            secret_key=self._cipher.encrypt(model.secret_key.encode()).decode(),
            passphrase=self._cipher.encrypt(model.passphrase.encode()).decode()
        )

    async def decrypt(self, model: SecretConfigDM) -> SecretConfigDM:
        """
        Decrypts sensitive fields in a SecretConfigDM model.

        This method takes an object containing encrypted API credentials and decrypts each field 
        using the configured Fernet cipher. It returns a new instance of SecretConfigDM with 
        plaintext values.

        Args:
            model (SecretConfigDM): The configuration object with encrypted credentials.

        Returns:
            SecretConfigDM: A new configuration object with decrypted credentials.

        Raises:
            ValueError: If decryption fails due to invalid input or corrupted data.
        """
        try:
            return SecretConfigDM.replace(  # type: ignore
                model,
                api_key=self._cipher.decrypt(model.api_key.encode()).decode(),
                secret_key=self._cipher.decrypt(model.secret_key.encode()).decode(),
                passphrase=self._cipher.decrypt(model.passphrase.encode()).decode()
            )
        except Exception as e:
            raise ValueError(f"Decryption error: {e}") from e

    async def get_signature(
        self, 
        params: SignatureDM
    ) -> dict[str, str]:
        """
        Generates OKX API signature headers for authenticated requests.

        This method constructs a signature using HMAC SHA256 based on the 
        concatenation of timestamp, HTTP method, request path, and request body.
        The resulting signature is Base64-encoded and returned along with the 
        timestamp in a dictionary suitable for use as HTTP headers.

        Args:
            params (SignatureDM): A data model containing the secret key, HTTP method, 
                                  request path, and optional request body.

        Returns:
            dict[str, str]: A dictionary containing 'OK-ACCESS-TIMESTAMP' and 'OK-ACCESS-SIGN'.
        """
        timestamp: str = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        pre_hash = timestamp + params.method.upper() + params.request_path + params.body
        signature = hmac.new(
            params.secret_key.encode('utf-8'),
            pre_hash.encode('utf-8'),
            hashlib.sha256
        ).digest()
        sign_base64 = base64.b64encode(signature).decode()
        return {
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-SIGN': sign_base64
        }

