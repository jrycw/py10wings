# 07
import logging
from functools import wraps


class log:
    def __init__(self, *, to_log=True):
        self.to_log = to_log

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.to_log:
                logging.info(
                    f'__call__ wrapper is called, {func=}, {args=}, {kwargs=}')
            return func(*args, **kwargs)
        return wrapper


def logf(func=None, /, *, to_log=True):
    if func is None:
        return log(to_log=to_log)
    return log(to_log=to_log)(func)


@logf()
def add1(a: int, b: int) -> int:
    """Take two integers and return their sum."""
    return a + b


@logf
def add2(a: int, b: int) -> int:
    """Take two integers and return their sum."""
    return a + b


class MyClass:
    @logf()
    def add1(self, a: int, b: int) -> int:
        """Take two integers and return their sum."""
        return a + b

    @logf
    def add2(self, a: int, b: int) -> int:
        """Take two integers and return their sum."""
        return a + b


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # print(add1(1, 2))  # 3
    # print(add2(1, 2))  # 3
    my_inst = MyClass()
    # print(my_inst.add1(1, 2))  # 3
    # print(my_inst.add2(1, 2))  # 3

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

    print(f'{add2=}')
    print(f'{add2.__module__=}')
    print(f'{add2.__name__=}')
    print(f'{add2.__doc__=}')
    print(f'{add2.__qualname__=}')
    print(f'{add2.__annotations__=}')
    print(f'{add2.__dict__=}')

    print(f'{my_inst.add2=}')
    print(f'{my_inst.add2.__module__=}')
    print(f'{my_inst.add2.__name__=}')
    print(f'{my_inst.add2.__doc__=}')
    print(f'{my_inst.add2.__qualname__=}')
    print(f'{my_inst.add2.__annotations__=}')
    print(f'{my_inst.add2.__dict__=}')
