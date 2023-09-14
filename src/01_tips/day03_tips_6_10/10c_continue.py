# 10c
def my_filter(func, iterable):
    """Emulate built-in filter"""
    if func is not None:
        return (item for item in iterable if func(item))
    return (item for item in iterable if item)
