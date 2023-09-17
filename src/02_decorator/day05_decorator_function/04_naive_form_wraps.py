# 04
from functools import wraps


def dec(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@dec
def my_func(*args: int, **kwargs: int) -> int:
    pass


if __name__ == '__main__':
    print(f'{my_func=}')
    print(f'{my_func.__module__=}')
    print(f'{my_func.__name__=}')
    print(f'{my_func.__doc__=}')
    print(f'{my_func.__qualname__=}')
    print(f'{my_func.__annotations__=}')
    print(f'{my_func.__dict__=}')
