# 08
import logging
from functools import wraps


def log(func=None, /, *, to_log=True):
    def dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if to_log:
                logging.info(f'wrapper is called, {func=}, {args=}, {kwargs=}')
            return func(*args, **kwargs)
        return wrapper

    if func is None:
        return dec
    return dec(func)


@log()
def add1(a: int, b: int) -> int:
    """Take two integers and return their sum."""
    return a + b


@log
def add2(a: int, b: int) -> int:
    """Take two integers and return their sum."""
    return a + b


class MyClass:
    @log()
    def add1(self, a: int, b: int) -> int:
        """Take two integers and return their sum."""
        return a + b

    @log
    def add2(self, a: int, b: int) -> int:
        """Take two integers and return their sum."""
        return a + b


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print(add1(1, 2))  # 3
    print(add2(1, 2))  # 3
    my_inst = MyClass()
    print(my_inst.add1(1, 2))  # 3
    print(my_inst.add2(1, 2))  # 3

    print(f'{add1=}')
    print(f'{add1.__module__=}')
    print(f'{add1.__name__=}')
    print(f'{add1.__doc__=}')
    print(f'{add1.__qualname__=}')
    print(f'{add1.__annotations__=}')
    print(f'{add1.__dict__=}')

    print(f'{my_inst.add1=}')
    print(f'{my_inst.add1.__module__=}')
    print(f'{my_inst.add1.__name__=}')
    print(f'{my_inst.add1.__doc__=}')
    print(f'{my_inst.add1.__qualname__=}')
    print(f'{my_inst.add1.__annotations__=}')
    print(f'{my_inst.add1.__dict__=}')
