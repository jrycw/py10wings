# 04
import random
from functools import wraps


def retry(func=None, /, max_retries=1):
    if not isinstance(max_retries, int) or max_retries < 0:
        raise ExceptionGroup('invalid max_retries',
                             (ValueError('max_retries must be an integer and >=0'),))

    def dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            exceptions = []
            runs = max_retries+1  # add the first invocation
            for i, _ in enumerate(range(runs), 1):
                print(f'{func.__name__} is running ({i}/{runs})')
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    exceptions.append(e)
            raise ExceptionGroup(
                f'Retry {max_retries} times but still failed', exceptions)
        return wrapper

    if func is None:
        return dec
    return dec(func)


@retry
def my_func():
    lot = random.choice([TypeError('1'), ValueError('2'),  'ok'])
    match lot:
        case TypeError():
            raise lot
        case ValueError():
            raise lot
        case _:
            return lot


if __name__ == '__main__':
    try:
        print(f'{my_func()=}')  # 'ok'
    except* Exception as eg:
        print(eg.exceptions)  # 4 possibilities
