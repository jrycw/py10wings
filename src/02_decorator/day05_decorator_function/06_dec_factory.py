# 06
import logging
from functools import wraps


def log(to_log=True):
    def dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if to_log:
                logging.info(f'wrapper is called, {func=}, {args=}, {kwargs=}')
            return func(*args, **kwargs)
        return wrapper
    return dec


@log(to_log=False)
def add(a: int, b: int) -> int:
    """Take two integers and return their sum."""
    return a + b


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print(f'{add=}')
    print(f'{add.__module__=}')
    print(f'{add.__name__=}')
    print(f'{add.__doc__=}')
    print(f'{add.__qualname__=}')
    print(f'{add.__annotations__=}')
    print(f'{add.__dict__=}')
