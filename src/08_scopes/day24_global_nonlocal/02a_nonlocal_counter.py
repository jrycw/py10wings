# 02a
from functools import wraps


# WRONG impl
def my_counter(fn):
    counts = 0

    @wraps(fn)
    def wrapper(*args, **kwargs):
        nonlocal counts
        counts += 1
        return fn(*args, **kwargs)

    wrapper.counts = counts
    return wrapper


@my_counter
def my_func():
    pass


my_func(), my_func()
print(my_func.counts)  # 0
