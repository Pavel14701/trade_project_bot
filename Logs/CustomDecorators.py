import time, warnings, logging, asyncio
from functools import wraps
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from User.LoadSettings import LoadUserSettingData

debug = LoadUserSettingData.load_debug_configs()

def deprecated(func):
    """Этот декоратор помечает функцию как устаревшую.
    При вызове функции будет выдано предупреждение."""
    @wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # Включаем предупреждение
        warnings.warn(f"Вызов устаревшей функции {func.__name__}.", category=DeprecationWarning, stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # Сбрасываем фильтр
        return func(*args, **kwargs)
    return new_func


class DeprecateMetaClass(type):
    def __new__(cls, name, bases, dct):
        for attr_name, attr_value in dct.items():
            if callable(attr_value):
                dct[attr_name] = deprecated(attr_value)
        return super().__new__(cls, name, bases, dct)


def retry_on_exception(max_retries:Optional[int], delay:Optional[int]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f'Attempt {attempt + 1} failed with exception: {e}/n Retrying in {delay} seconds...')
                    last_exception = e
                    time.sleep(delay)
            raise last_exception(f'Failed after {max_retries} retries')
        return wrapper
    return decorator


def retry_on_exception_async(max_retries:Optional[int], delay:Optional[int]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    print(f'Attempt {attempt + 1} failed with exception: {e}\nRetrying in {delay} seconds...')
                    await asyncio.sleep(delay)
                    last_exception = e
            raise last_exception
        return wrapper
    return decorator


def log_exceptions_async(logger: logging.Logger):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                function_name = func.__name__
                session = None
                for arg in args:
                    if isinstance(arg, AsyncSession):
                        session = arg
                        break
                if not session:
                    for key, value in kwargs.items():
                        if isinstance(value, AsyncSession):
                            session = value
                            break
                if args and hasattr(args[0], '__class__'):
                    class_name = args[0].__class__.__name__
                    logger.error(f"Error in {class_name}.{function_name}: {e}")
                    if class_name == 'DataAllDatasetsAsync' or 'AsyncStateRequest' and session:
                        await session.rollback()
                else:
                    logger.error(f"Error in {function_name}: {e}")
                if debug:
                    raise e
        return wrapper
    return decorator


def log_exceptions(logger:logging.Logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                function_name = func.__name__
                session = None
                for arg in args:
                    if isinstance(arg, sessionmaker):
                        session = arg
                        break
                if not session:
                    for key, value in kwargs.items():
                        if isinstance(value, sessionmaker):
                            session = value
                            break
                if args and hasattr(args[0], '__class__'):
                    class_name = args[0].__class__.__name__
                    logger.error(f"Error in {class_name}.{function_name}: {e}")
                    if class_name == 'DataAllDatasets' or 'StateRequest' and session:
                        session.rollback()
                else:
                    logger.error(f"Error in {function_name}: {e}")
                if debug:
                    raise e
        return wrapper
    return decorator