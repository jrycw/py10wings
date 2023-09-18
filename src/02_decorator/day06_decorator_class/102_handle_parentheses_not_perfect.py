# 102
import logging
from functools import update_wrapper
from types import MethodType


class log:
    def __init__(self, func=None, /, *, to_log=True):
        self.func = func
        self.to_log = to_log
        if func is not None:
            update_wrapper(self, func)

    def _make_wrapper(self, func):
        def wrapper(*args, **kwargs):
            if self.to_log:
                logging.info(
                    f'__call__ inner is called, {func=}, {args=}, {kwargs=}')
            return func(*args, **kwargs)
        return wrapper

    def __call__(self, *args, **kwargs):
        if self.func is None:
            func = args[0]
            wrapper = self._make_wrapper(func)
            update_wrapper(wrapper, func)
            return wrapper
        else:
            func = self.func
            wrapper = self._make_wrapper(func)
            return wrapper(*args, **kwargs)

    def __get__(self, instance, owner_class):
        if instance is None:
            return self
        return MethodType(self, instance)


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

    print(f'{add2=}')
    print(f'{add2.__module__=}')
    print(f'{add2.__name__=}')
    print(f'{add2.__doc__=}')
    print(f'{add2.__qualname__=}')
    print(f'{add2.__annotations__=}')
    print(f'{add2.__dict__=}')
