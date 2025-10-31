"""
Defines structured data models used for authentication and request signing in the OKX integration layer.

This module includes:
- `BaseDataClass`: A frozen base class with utility methods for serialization and field replacement.
- `SecretConfigDM`: An immutable dataclass representing sensitive API credentials.
- `SignatureDM`: A mutable dataclass used for constructing request signatures.

These entities are designed to be lightweight, type-safe, and compatible with serialization and cryptographic workflows.
"""


from dataclasses import asdict, dataclass
from typing import Any, Self


@dataclass(slots=True, frozen=True)
class BaseDataClass:
    """
    Base class for immutable dataclasses with utility methods.

    Provides:
    - `to_dict()`: Converts the dataclass instance to a dictionary.
    - `replace()`: Creates a new instance with updated fields.

    This class is intended to be subclassed by other data models that require immutability and convenience methods.
    """

    def to_dict(self) -> dict[str, Any]:
        """
        Serializes the dataclass instance into a dictionary.

        Returns:
            dict[str, Any]: A dictionary representation of the instance.
        """
        return asdict(self)

    @classmethod
    def replace(cls, instance: Self, **kwargs: Any) -> Self:
        """
        Creates a new instance of the dataclass with updated fields.

        Args:
            instance (Self): The original dataclass instance.
            **kwargs (Any): Fields to override in the new instance.

        Returns:
            Self: A new instance with updated values.
        """
        return cls(**{**instance.to_dict(), **kwargs})


@dataclass(slots=True, frozen=True)
class SecretConfigDM(BaseDataClass):
    """
    Immutable data model for storing sensitive API credentials required for authenticated requests.

    Attributes:
        user_id (int): Internal user identifier.
        api_key (str): Public API key for authentication.
        secret_key (str): Private secret key used for request signing.
        passphrase (str): Additional passphrase required by OKX API.
    """
    user_id: int
    api_key: str
    secret_key: str
    passphrase: str


@dataclass(slots=True)
class SignatureDM:
    """
    Mutable data model used for constructing request signatures.

    This model holds the necessary components for generating a cryptographic signature
    for an HTTP request to the OKX API.

    Attributes:
        secret_key (str): Secret key used for HMAC or other signing algorithms.
        method (str): HTTP method (e.g., GET, POST).
        request_path (str): API endpoint path.
        body (str): Optional request body content (default is empty string).
    """
    secret_key: str 
    method: str
    request_path: str 
    body: str = ''