# 01
def dec(func):
    return func


def my_func():
    pass


if __name__ == '__main__':
    orig_func_id = id(my_func)
    my_func = dec(my_func)
    deced_func_id = id(my_func)
    print(orig_func_id == deced_func_id)  # True
