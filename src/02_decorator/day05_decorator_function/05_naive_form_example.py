# 05
import logging
from functools import wraps


def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f'wrapper is called, {func=}, {args=}, {kwargs=}')
        return func(*args, **kwargs)
    return wrapper


@log
def add(a: int, b: int) -> int:
    return a + b


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print(add(1, 2))  # 3
