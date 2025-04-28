from dataclasses import dataclass


class DomainException(Exception):
    """Base exception for domain-related errors."""
    pass


@dataclass
class UserNotFoundException(DomainException):
    """Exception raised when a user is not found."""
    message: str = "User not found"


@dataclass
class InvalidPasswordException(DomainException):
    """Exception raised when a password is incorrect."""
    message: str = "Invalid password"


@dataclass
class UserGetManyConnections(DomainException):
    """Exception raised when a user exceeds the connection limit."""
    message: str = "Connection limit reached"


@dataclass
class UserAlreadyExistsError(DomainException):
    """Exception raised when a user with the given username already exists."""
    message: str = "A user with this username already exists in the system"
