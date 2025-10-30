"""
Defines an abstract base class for constructing and executing authenticated HTTP requests to the OKX API.

This module provides the `BaseQuerySet` class, which serves as a reusable foundation for building
query interfaces that interact with OKX endpoints. It supports both GET and POST methods, handles
parameter serialization, and integrates request signing via a pluggable `ISignature` interface.

Key Features:
- Converts DTOs into query parameters or request bodies.
- Builds signed headers using secret credentials.
- Executes asynchronous HTTP requests using a generic client.
- Provides high-level `get()` and `post()` methods for convenience.

Type Parameters:
    TClient: A client class responsible for making asynchronous HTTP requests (e.g., based on httpx).
    TConsts: A constants class containing configuration values such as base URLs.

Intended Usage:
    Subclass `BaseQuerySet` to implement specific query sets for different OKX domains (e.g., market, trade).
    Inject a client, constants, and optional signature logic to enable secure and structured API communication.

Dependencies:
    - DTOs from `api_okx_v1.src.application.dto.base`
    - Signature interface from `api_okx_v1.src.application.interfaces`
    - Signature data model from `api_okx_v1.src.domain.entities`
    - Type definitions from `api_okx_v1.src.infrastructure._types`
"""


from abc import ABC, abstractmethod
from typing import Any, Generic
import json

from api_okx_v1.src.application.dto.base import BaseDataClass, SecretDTO
from api_okx_v1.src.application.interfaces import ISignature
from api_okx_v1.src.domain.entities import SignatureDM
from api_okx_v1.src.infrastructure._types import TClient, TConsts


class BaseQuerySet(Generic[TClient, TConsts], ABC):
    """
    Abstract base class for constructing and executing HTTP queries to the OKX API.

    This class provides a structured interface for sending authenticated GET and POST requests,
    handling parameter preparation, and generating signed headers for secure communication.

    Type Parameters:
        TClient: A subclass of `AsyncClient` responsible for making asynchronous HTTP requests.
        TConsts: A subclass of `OkxBaseConsts` containing constant values such as base URLs.
    """

    @abstractmethod
    def __init__(
        self,
        client: TClient,
        consts: TConsts,
        security: ISignature | None
    ) -> None:
        """
        Initializes the query set with a client, constants, and optional security handler.

        Args:
            client (TClient): An asynchronous HTTP client used to perform requests.
            consts (TConsts): A constants object containing configuration values like base URL.
            security (ISecurity | None): Optional security interface for signing requests.
        """
        raise NotImplementedError()

    async def _prepare_query_params(
        self,
        dto: BaseDataClass
    ) -> dict[str, Any]:
        """
        Converts a data transfer object (DTO) into a dictionary of query parameters,
        excluding any fields with `None` values.

        Args:
            dto (BaseDataClass): A DTO instance containing request parameters.

        Returns:
            dict[str, Any]: A dictionary of non-null parameters suitable for query strings or request bodies.
        """
        return {k: v for k, v in dto.to_dict().items() if v is not None}

    async def _build_signed_headers(
        self,
        method: str,
        endpoint: str,
        body_str: str,
        secret: SecretDTO | None
    ) -> dict[str, str]:
        """
        Constructs request headers including authentication signature if a secret is provided.

        Args:
            method (str): HTTP method (e.g., "GET", "POST").
            endpoint (str): API endpoint path.
            body_str (str): JSON-encoded string of the request body.
            secret (SecretDTO | None): Optional secret credentials for signing the request.

        Returns:
            dict[str, str]: A dictionary of HTTP headers including signature and authentication keys.
        """
        headers = {"Content-Type": "application/json"}
        if secret and self._security:
            signature_headers = await self._security.get_signature(SignatureDM(
                secret_key=secret.secret_key,
                method=method,
                request_path=endpoint,
                body=body_str
            ))
            headers.update({
                "OK-ACCESS-KEY": secret.api_key,
                "OK-ACCESS-PASSPHRASE": secret.passphrase,
                **signature_headers
            })
        return headers

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        secret: SecretDTO | None = None
    ) -> dict[str, Any]:
        """
        Executes an HTTP request to the specified endpoint using the provided method and parameters.

        Args:
            method (str): HTTP method ("GET" or "POST").
            endpoint (str): API endpoint path.
            params (dict[str, Any] | None): Query parameters for GET requests.
            body (dict[str, Any] | None): Request body for POST requests.
            secret (SecretDTO | None): Optional secret for signing the request.

        Returns:
            dict[str, Any]: Parsed JSON response from the API.

        Raises:
            ValueError: If the HTTP method is unsupported.
            HTTPError: If the response status indicates an error.
        """
        self._consts: TConsts
        self._security: ISignature
        self._client: TClient
        url = f"{self._consts.BASE_URL}{endpoint}"
        body_str = json.dumps(body) if body else ""
        headers = await self._build_signed_headers(method, endpoint, body_str, secret)
        if method.upper() == "GET":
            response = await self._client.get(url, params=params, headers=headers)
        elif method.upper() == "POST":
            response = await self._client.post(url, content=body_str, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        response.raise_for_status()
        return response.json()

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | BaseDataClass | None = None,
        secret: SecretDTO | None = None
    ) -> dict[str, Any]:
        """
        Sends a GET request to the specified endpoint with optional query parameters and authentication.

        Args:
            endpoint (str): API endpoint path.
            params (dict[str, Any] | BaseDataClass | None): Query parameters or DTO.
            secret (SecretDTO | None): Optional secret for signing the request.

        Returns:
            dict[str, Any]: Parsed JSON response from the API.
        """
        if isinstance(params, BaseDataClass):
            params = await self._prepare_query_params(params)
        return await self._request("GET", endpoint, params=params, secret=secret)

    async def post(
        self,
        endpoint: str,
        params: dict[str, Any] | BaseDataClass,
        secret: SecretDTO | None = None
    ) -> dict[str, Any]:
        """
        Sends a POST request to the specified endpoint with a request body and optional authentication.

        Args:
            endpoint (str): API endpoint path.
            body (dict[str, Any] | BaseDataClass): Request payload or DTO.
            secret (SecretDTO | None): Optional secret for signing the request.

        Returns:
            dict[str, Any]: Parsed JSON response from the API.
        """
        if isinstance(params, BaseDataClass):
            params = await self._prepare_query_params(params)
        return await self._request("POST", endpoint, body=params, secret=secret)