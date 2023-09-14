# 06a
def get_bool(iterable):
    if len(iterable) > 10:
        return True
    else:
        return False


if __name__ == '__main__':
    print(get_bool(range(10)), get_bool(range(11)))    # False, True
