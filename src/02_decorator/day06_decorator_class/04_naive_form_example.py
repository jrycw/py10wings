# 04
import logging
from functools import update_wrapper
from types import MethodType


class log:
    def __init__(self, func):
        self.func = func
        update_wrapper(self, self.func)

    def __call__(self, *args, **kwargs):
        logging.info(f'__call__ is called, {self.func=}, {args=}, {kwargs=}')
        return self.func(*args, **kwargs)

    def __get__(self, instance, owner_class):
        if instance is None:
            return self
        return MethodType(self, instance)


@log
def add(a: int, b: int) -> int:
    """Take two integers and return their sum."""
    return a + b


class MyClass:
    @log
    def add(self, a: int, b: int) -> int:
        """Take two integers and return their sum."""
        return a + b


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    my_inst = MyClass()
    print(add(1, 2))  # 3
    print(my_inst.add(1, 2))  # 3

    print(f'{add=}')
    print(f'{add.__module__=}')
    print(f'{add.__name__=}')
    print(f'{add.__doc__=}')
    print(f'{add.__qualname__=}')
    print(f'{add.__annotations__=}')
    print(f'{add.__dict__=}')

    print(f'{my_inst.add=}')
    print(f'{my_inst.add.__module__=}')
    print(f'{my_inst.add.__name__=}')
    print(f'{my_inst.add.__doc__=}')
    print(f'{my_inst.add.__qualname__=}')
    print(f'{my_inst.add.__annotations__=}')
    print(f'{my_inst.add.__dict__=}')
