class DomainException(Exception):
    """Базовое исключение для ошибок в предметной области."""
    pass


class UserNotFoundException(DomainException):
    """Ошибка, если пользователь не найден."""
    def __init__(self, message="Пользователь не найден"):
        super().__init__(message)


class InvalidPasswordException(DomainException):
    """Ошибка, если пароль неверен."""
    def __init__(self, message="Неверный пароль"):
        super().__init__(message)


class UserGetManyConnections(DomainException):
    """Ошибка, если у пользователя больше 2 подключений в категории"""
    def __init__(self, message="Достигнут лимит подключений"):
        super().__init__(message)


class UserAlreadyExistsError(DomainException):
    "Ошибка, если пользователь с таким юзернеймом есть"
    def __init__(self, message="Пользователь с таким юзернеймом уже есть в системе"):
        super().__init__(message)