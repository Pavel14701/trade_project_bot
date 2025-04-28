from typing import Protocol, Generic
from uuid import UUID

from fastapi import Request, Response

from main_app.src.domain.entities import (
    PasswordDM,
    SignupPasswordDM, 
    UserDm, 
    UserPasswordDM,
    UserSignupDM,
    WebSocketDM
)
from main_app.src.infrastructure.types import (
    SessionID,
    ExceptionType, 
    GuestSessionData, 
    GuestSessionID, 
    SessionModel
)

class IUser(Protocol):
    """Interface for user management."""

    async def get_password(self, username: str) -> UserPasswordDM:
        """Retrieves the hashed password of a user by their username."""
        ...

    async def signup(self, signup_dm: UserSignupDM) -> None:
        """Registers a new user."""
        ...

    async def get_current_user(self, user_id: int) -> UserDm:
        """Returns the current user's data by their ID."""
        ...

    async def get_user_by_username(self, username: str) -> UserDm:
        """Returns the current user's data by their Username."""
        ...

class ISecurity(Protocol):
    """Interface for password security management."""

    async def verify_password(self, password: PasswordDM) -> None:
        """Verifies the correctness of a password."""
        ...

    async def hash_password(self, model: SignupPasswordDM) -> PasswordDM:
        """Hashes a password before storing it."""
        ...


class IOkxListner(Protocol):
    """Interface for managing OKX WebSocket configurations."""

    async def save_okx_listner_config(self, config: WebSocketDM) -> None:
        """Saves the WebSocket configuration."""
        ...

    async def get_ls_configs(self, user_id: int) -> list[WebSocketDM]:
        """Retrieves a list of WebSocket configurations for a user."""
        ...


class IConfigEncryption(Protocol):
    """Interface for encrypting and decrypting configurations."""

    async def encrypt(self, model: WebSocketDM) -> WebSocketDM:
        """Encrypts WebSocket configuration data."""
        ...

    async def decrypt(self, model: WebSocketDM) -> WebSocketDM:
        """Decrypts WebSocket configuration data."""
        ...


class ISession(Protocol):
    """Interface for session transaction management."""

    async def commit(self) -> None:
        """Commits changes in the session."""
        ...

    async def flush(self) -> None:
        """Flushes changes without committing the transaction."""
        ...

    async def rollback(self) -> None:
        """Rolls back changes in the session."""
        ...


class IErrorHandler(Protocol, Generic[ExceptionType]):
    """Interface for error handling."""

    def handle_error(
        self, 
        error: Exception,
        _raise: type[ExceptionType]
    ) -> (type[ExceptionType] | type[Exception]):
        """Handles an error and raises an appropriate exception."""
        ...


class ISessionBackend(Protocol, Generic[SessionID, SessionModel]):
    """Abstract class that defines methods for interacting with session data."""
    async def create(self, session_id: SessionID, data: SessionModel) -> None:
        """Create a new session."""
        ...

    async def read(self, session_id: SessionID) -> SessionModel | None:
        """Read session data from the storage."""
        ...

    async def update(self, session_id: SessionID, data: SessionModel) -> None:
        """Update session data to the storage"""
        ...

    async def delete(self, session_id: SessionID) -> None:
        """Remove session data from the storage."""
        ...


class IGuestSessionBackend(Protocol, Generic[GuestSessionID, GuestSessionData]):
    """Abstract interface for managing guest sessions."""

    def create_guest_session(self, response: Response) -> GuestSessionID:
        """Creates a new guest session and stores it in a cookie."""
        ...

    def get_guest_session(self, request: Request) -> GuestSessionID | None:
        """Gets the current guest session from the cookie."""
        ...

    def delete_guest_session(self, response: Response) -> None:
        """Deletes a guest session (clears cookies)."""
        ...

    def update_guest_data(
        self, 
        request: Request, 
        response: Response, 
        new_data: GuestSessionData
    ) -> None:
        """Updates guest data while preserving existing data."""
        ...

    def get_guest_data(self, request: Request) -> GuestSessionData:
        """Gets guest session data from cookies."""
        ...


class ICookieBackend(Protocol):
    """Interface for managing cookies: guest and authorized sessions."""

    def set_cookie(
        self, 
        response: Response, 
        key: str, 
        value: str, 
        max_age: int
    ) -> None:
        """Sets or updates cookies."""
        ...

    def get_cookie(self, request: Request, key: str) -> str | None:
        """Gets the cookie value."""
        ...

    def delete_cookie(self, response: Response, key: str) -> None:
        """Clears the cookie by setting it to an empty value."""
        ...


class UUIDGenerator(Protocol):
    """Protocol for callable UUID generators."""

    def __call__(self) -> UUID:
        """Generates a new UUID."""
        ...
