from functools import wraps


def postman(item):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            print(f'{item=} is received')
            return fn(*args, **kwargs)
        return wrapper
    return decorator
