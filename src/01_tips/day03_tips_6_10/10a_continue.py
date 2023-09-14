# 10a
def func(x):
    try:
        return x > 10
    except TypeError:
        return False


def my_filter(func, iterable):
    """`yield item` locates at the second level of indentation"""
    for item in iterable:
        if func(item):
            yield item


if __name__ == '__main__':
    flt = my_filter(func, [2, 11, 'str', (), []])
    print(list(flt))  # [11]
