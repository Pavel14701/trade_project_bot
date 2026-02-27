from sqlalchemy.exc import IntegrityError # type: ignore

from application.exceptions import DomainException
from application.interfaces import IErrorHandler


class ExceptionHandlersRepo(IErrorHandler[DomainException]):
    """Repository for handling application exceptions."""

    def handle_error(
        self, 
        error: Exception,
        _raise: type[DomainException]
    ) -> (type[DomainException] | type[Exception]):
        """Determines the appropriate exception type to raise."""
        return _raise if isinstance(error, IntegrityError) else type(error)
