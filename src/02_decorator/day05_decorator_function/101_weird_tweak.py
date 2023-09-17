# 101
from functools import wraps


def dec(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        args = (arg+1 for arg in args)
        return func(*args, **kwargs)
    return wrapper


@dec
def add(a: int, b: int) -> int:
    return a + b


if __name__ == '__main__':
    print(add(1, 2))  # 5
