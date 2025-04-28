from dataclasses import is_dataclass
from typing import Awaitable, Callable, Protocol, TypeVar
from uuid import UUID

from fastapi import Request, Response

from main_app.src.application.exceptions import DomainException


class DataclassProtocol(Protocol):
    """A protocol enforcing that subclasses must be dataclasses.

    This protocol ensures that any class inheriting from it is a dataclass.
    If a subclass is not a dataclass, a TypeError is raised during class definition.

    Purpose:
    - Helps enforce type safety by guaranteeing that certain models are structured
      as dataclasses.
    - Ensures compatibility with serialization methods that rely on 
      dataclasses (e.g., `asdict`).
    - Useful for defining type constraints in generic TypeVars for session models, 
      domain models, and DTOs.

    Example:
    >>> from dataclasses import dataclass
    >>> @dataclass
    ... class UserData(DataclassProtocol):
    ...     username: str
    ...     age: int
    >>> UserData(username="Alice", age=30)  # ✅ Works as expected

    >>> class InvalidClass(DataclassProtocol):
    ...     pass
    >>> # ❌ Raises TypeError: "InvalidClass must be dataclass!"
    """

    def __init_subclass__(cls):
        if not is_dataclass(cls):
            raise TypeError(f"{cls.__name__} must be dataclass!")


SessionModel = TypeVar("SessionModel", bound=DataclassProtocol)
SessionID = TypeVar("SessionID", bound=UUID, contravariant=True)

GuestSessionID = TypeVar("GuestSessionID", bound=UUID, covariant=True)
GuestSessionData = TypeVar("GuestSessionData", bound=DataclassProtocol)

ExceptionType = TypeVar("ExceptionType", bound=DomainException)

RequestResponseEndpoint = Callable[[Request], Awaitable[Response]]

DomainModel = TypeVar("DomainModel", bound=DataclassProtocol)
DtoModel = TypeVar("DtoModel", bound=DataclassProtocol)