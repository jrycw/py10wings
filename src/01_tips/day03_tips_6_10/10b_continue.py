# 10b
def func(x):
    try:
        return x > 10
    except TypeError:
        return False


def my_filter(func, iterable):
    """`yield item` locates at the first level of indentation
        by using `continue` to save one level of indentation"""
    for item in iterable:
        if not func(item):
            continue
        yield item


if __name__ == '__main__':
    flt = my_filter(func, [2, 11, 'str', (), []])
    print(list(flt))  # [11]
