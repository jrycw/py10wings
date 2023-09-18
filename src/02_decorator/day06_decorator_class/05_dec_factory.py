# 05
import logging
from functools import wraps


class log:
    def __init__(self, to_log=True):
        self.to_log = to_log

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.to_log:
                logging.info(
                    f'__call__ wrapper is called, {func=}, {args=}, {kwargs=}')
            return func(*args, **kwargs)
        return wrapper


@log()
def add(a: int, b: int) -> int:
    """Take two integers and return their sum."""
    return a + b


class MyClass:
    @log()
    def add(self, a: int, b: int) -> int:
        """Take two integers and return their sum."""
        return a + b

    def add2(self):
        pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    my_inst = MyClass()
    print(add(1, 2))  # 3
    print(my_inst.add(1, 2))  # 3

    # print(f'{add=}')
    # print(f'{add.__module__=}')
    # print(f'{add.__name__=}')
    # print(f'{add.__doc__=}')
    # print(f'{add.__qualname__=}')
    # print(f'{add.__annotations__=}')
    # print(f'{add.__dict__=}')

    # print(f'{my_inst.add=}')
    # print(f'{my_inst.add.__module__=}')
    # print(f'{my_inst.add.__name__=}')
    # print(f'{my_inst.add.__doc__=}')
    # print(f'{my_inst.add.__qualname__=}')
    # print(f'{my_inst.add.__annotations__=}')
    # print(f'{my_inst.add.__dict__=}')
