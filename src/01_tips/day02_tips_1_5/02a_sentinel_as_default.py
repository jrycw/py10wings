# 02a
def get_given(given=None, default=0):
    return default if given is None else given


if __name__ == '__main__':
    print(get_given('abc'))  # 'abc'
    print(get_given(None, 2))  # 2
