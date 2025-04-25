import time, warnings, logging, asyncio
from functools import wraps
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from configs.load_settings import ConfigsProvider


debug_logging_settings=ConfigsProvider().load_debug_logging_configs()


def deprecated(func):
    """Этот декоратор помечает функцию как устаревшую.
    При вызове функции будет выдано предупреждение."""
    @wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)
        warnings.warn(f"Вызов устаревшей функции {func.__name__}.", category=DeprecationWarning, stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)
        return func(*args, **kwargs)
    return new_func


class DeprecateMetaClass(type):
    def __new__(cls, name, bases, dct):
        for attr_name, attr_value in dct.items():
            if callable(attr_value):
                dct[attr_name] = deprecated(attr_value)
        return super().__new__(cls, name, bases, dct)


def retry_on_exception(
    logger:logging.Logger, max_retries:int=debug_logging_settings['max_retries'],
    delay:int=debug_logging_settings['delay']):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f'Attempt {attempt + 1} failed with exception: {e}\n Retrying in {delay} seconds...')
                    print(f'Attempt {attempt + 1} failed with exception: {e}\n Retrying in {delay} seconds...')
                    time.sleep(delay)
                    if attempt == max_retries:
                        raise e(f'Failed after {max_retries} retries')
        return wrapper
    return decorator


def retry_on_exception_async(
    logger:logging.Logger, max_retries:int=debug_logging_settings['max_retries'],
    delay:int=debug_logging_settings['delay']):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.error(f'Attempt {attempt + 1} failed with exception: {e}\n Retrying in {delay} seconds...')
                    print(f'Attempt {attempt + 1} failed with exception: {e}\n Retrying in {delay} seconds...')
                    await asyncio.sleep(delay)
                    if attempt == max_retries:
                        raise e(f'Failed after {max_retries} retries')
        return wrapper
    return decorator


def log_exceptions_async(
    logger:logging.Logger, create_logging:Optional[bool]=debug_logging_settings['write_logs'],
    debug:bool=debug_logging_settings['debug']
    ):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not create_logging:
                return
            session = None
            for arg in args:
                if isinstance(arg, AsyncSession):
                    session = arg
                    break
            function_name = func.__name__
            if args and hasattr(args[0], '__class__'):
                class_name = args[0].__class__.__name__
                if class_name == 'DataAllDatasetsAsync' or 'AsyncStateRequest' and session:
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        logger.error(f"Error in {function_name}: {e}")
                        await session.rollback()
                        if debug:
                            raise e
                    finally:
                        await session.aclose()
            else:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in {function_name}: {e}")
                    if debug:
                        raise e
        return wrapper
    return decorator


def log_exceptions(logger: logging.Logger, create_logging: Optional[bool] = debug_logging_settings['write_logs'], debug: bool = debug_logging_settings['debug']):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not create_logging:
                return func(*args, **kwargs)
            session = None
            for arg in args:
                if isinstance(arg, sessionmaker):
                    session = arg
                    break
            function_name = func.__name__
            if args and hasattr(args[0], '__class__'):
                class_name = args[0].__class__.__name__
                if class_name == 'DataAllDatasets' or 'StateRequest' and session:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        function_name = func.__name__
                        logger.error(f"Error in {function_name}: {e}")
                        session.rollback()
                        if debug:
                            raise e
                    finally:
                        session.close()
            else:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in {function_name}: {e}")
                    if debug:
                        raise e
        return wrapper
    return decorator