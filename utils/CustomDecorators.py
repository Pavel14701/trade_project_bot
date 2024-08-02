import warnings
import functools
import time
from httpx import ReadTimeout
from httpcore import ConnectTimeout


def deprecated(func):
    """Этот декоратор помечает функцию как устаревшую.
    При вызове функции будет выдано предупреждение."""
    @functools.wraps(func)
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
    

def retry(max_retries):
    def decorator(original_func):
        def wrapper(*args, **kwargs):
            attempts = 0
            last_exception = None
            while attempts < max_retries:
                try:
                    result = original_func(*args, **kwargs)
                    return result
                except (ReadTimeout, ConnectTimeout) as e:
                    print(f"Попытка {attempts + 1} завершилась неудачей: {e}")
                    time.sleep(5)
                    attempts += 1
                    last_exception = e
            raise ReadTimeout from last_exception
        return wrapper
    return decorator