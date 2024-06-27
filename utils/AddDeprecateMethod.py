from functools import singledispatchmethod
import warnings
import functools


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


class MyMeta(type):
    def __new__(cls, name, bases, dct):
        for attr_name, attr_value in dct.items():
            if callable(attr_value):
                dct[attr_name] = deprecated(attr_value)
        return super().__new__(cls, name, bases, dct)



"""
class Shape(metaclass=MyMeta):
    def __init__(self, name):
        self.name = name

class Circle(Shape):
    pass

class Square(Shape):
    pass


class Triangle(Shape):
    pass

class MyClass:
    @singledispatchmethod
    def process(self, shape):
        raise NotImplementedError("Unsupported shape type")

    @process.register
    def _(self, shape: Circle):
        print(f"Processing circle: {shape.name}")

    
    @process.register
    def _(self, shape: Square):
        print(f"Processing square: {shape.name}")

obj = MyClass()
circle = Circle("Circle1")
square = Square("Square1")
triangle = Triangle("Triangle")
obj.process(circle)
obj.process(square)
obj.process(triangle)
"""