from sqlalchemy.exc import IntegrityError

from main_app.src.application.exceptions import DomainException
from main_app.src.application.interfaces import IErrorHandler


class ExceptionHandlersRepo(IErrorHandler[DomainException]):
    """Repository for handling application exceptions."""

    def handle_error(
        self, 
        error: Exception,
        _raise: type[DomainException]
    ) -> (type[DomainException] | type[Exception]):
        """Determines the appropriate exception type to raise."""
        return _raise if isinstance(error, IntegrityError) else type(error)
