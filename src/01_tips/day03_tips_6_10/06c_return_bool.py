# 06c
def get_bool(iterable):
    return len(iterable) > 10


if __name__ == '__main__':
    print(get_bool(range(10)), get_bool(range(11)))    # False, True
